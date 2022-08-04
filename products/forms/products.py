"""
    Forms customization
"""

import extra_views
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row
from django import forms
from django.db import transaction
from django.template.exceptions import TemplateSyntaxError
from django.utils import timezone

from investment import models as invest_models

from .. import models


class AgreementForm(forms.ModelForm):
    """
    Agreement form
    """

    class Meta:
        """
        Meta class
        """
        model = models.AgreementTemplate
        fields = "__all__"
        widgets = {
            'instruction': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._set_layout()

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        try:
            # TODO: review
            application = invest_models.Application.objects.get(
                product=cleaned_data['product'])
            agrement_render = application.application_class.get_agreement_class()
            agrement_render.render(
                user=None, agreement_text=text, preview=True)
        except TemplateSyntaxError as err:
            self.add_error(
                'text', f"Erro ao salvar texto do contrato. Mensagem original: {str(err)}")
        return cleaned_data

    def _set_layout(self):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name'),
                Column('product'),
                Column('display_text'),
            ),
            Row(
                Column('type'),
                Column('term_value'),
                Column('term_unit'),
            ),
            Row(
                Column(Field('text', rows=15)),
            ),
            Row(
                Column(self._instructions()),
            ),
        )

    def _instructions(self):
        # pylint: disable=no-member
        applications = invest_models.Application.objects.all()
        tags_html = ''
        for application in applications:
            tags = application.application_class.get_agreement_class().available_tags()
            tags_str = f'{"}}, {{".join(tags)}'
            tags_html += '<p id="tag_$id" class="agreement_tag"> $prod: {% verbatim %} {{ $tags }} {% endverbatim %} </p>'.replace(
                '$tags', tags_str).replace('$id', str(application.product.pk)).replace("$prod", application.product.display_text)

        instructions = '''
        <p class=""> Substitua as tags abaixo no texto como são apresentadas <p>
        <p class=""> Exemplo: {% verbatim %} {{nome}} {% endverbatim %} será substituída pelo nome do usuário/cliente <p>
        <p class="fw-bold"> Tags por produto: </p>
        ''' + tags_html

        text = HTML(instructions)
        return text


class PurchaseForm(forms.Form):
    """
    Purchase form
    """

    product = forms.IntegerField(widget=forms.HiddenInput())

    # Fields added in child classes which will be used to build agreements
    extra_args_fields = []

    def __init__(self, *args, **kwargs) -> None:
        self.product = kwargs.pop('product', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['product'].required = True
        self.fields['product'].initial = self.product.pk
        self.helper = FormHelper()

    def clean(self):
        cleaned_data = super().clean()

        cleaned_data['product'] = self.product
        product = self.product

        if product:
            if product.purchased:
                self.add_error('product', "Este produto já foi contratado")

            # Only users with investor profile can purchase a product
            investor_profile = self.user.investorprofile_set.last()
            if not investor_profile:
                self.add_error(
                    'product',
                    (
                        'Seu perfil de investidor não está definido. '
                        'Faça o teste de perfil no menu "Consultas / Perfil de investiento"'
                    )
                )
                return cleaned_data

            # Investor profile must match one of the product profiles
            if not product.profileproduct_set.filter(profile=investor_profile.profile).exists():
                self.add_error(
                    'product', f'Você não tem acesso a este produto ({product.display_text})')
                return cleaned_data

            # Product is available only if it has anassociated agreement
            agreement_template = product.agreementtemplate_set.last()
            if not agreement_template or not investor_profile:
                self.add_error('product', 'Produto indisponível no momento.')
                return cleaned_data

        else:
            self.add_error('product', 'A escolha do produto é obrigatória')

        return cleaned_data

    def save(self, commit=True):
        """
        Create a product purchase
        """
        cleaned_data = self.cleaned_data
        product = cleaned_data['product']

        agreement_template = product.agreementtemplate_set.filter(
            type=self.user.client.type).last()

        term = agreement_template.term

        date_created = timezone.localtime(timezone.now())

        obj = models.ProductPurchase(
            user=self.user,
            product=product,
            agreement_template=agreement_template,
            agreement=self._render_agreement(product, agreement_template, cleaned_data),
            date_purchased=date_created,
            date_expire=date_created + term if term else None,
            notify_before_end=True
        )

        if commit:
            with transaction.atomic():
                obj.save()
                self.create_application_account(obj)
                self.post_created(obj)
        return obj

    def _render_agreement(self, product, agreement_template, cleaned_data):
        agreement_renderer = product.application.application_class.get_agreement_class()
        extra_args = dict()
        for field_name in self.extra_args_fields:
            extra_args[field_name] = cleaned_data[field_name]
        return agreement_renderer.render(self.user, agreement_template.text, extra_args=extra_args)


    def create_application_account(self, product_purchase):
        """
        Creates an application account according to the product
        """
        # pylint: disable=no-member
        app_acc = invest_models.ApplicationAccount.objects.create(
            application=product_purchase.product.application,
            user=self.user,
            operator=self.user
        )
        app_acc.post_create()
        product_purchase.application_account = app_acc
        product_purchase.save()

    def post_created(self, product_purchase):
        """
        Called after product is purchased and application account is created
        Extra operations may be implemented here
        """


class ProfileProductItem(extra_views.InlineFormSetFactory):
    """
    Inline formset for profile product registering
    """
    model = models.ProfileProduct
    fields = "__all__"


class DashboardProductItem(extra_views.InlineFormSetFactory):
    """
    Inline formset for profile product registering
    """
    model = models.ProductDashboard
    fields = "__all__"


class ProductForm(forms.ModelForm):
    """
    Purchase form
    """

    is_active = forms.BooleanField(label="Ativo", required=False)

    class Meta:
        """
        Meta class
        """
        model = models.Product
        fields = '__all__'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        choices = invest_models.Application.objects.filter(
            product__isnull=True, is_active=True).values_list('pk', 'display_text')

        if not self.instance.pk:
            if choices:
                self.fields['application'].choices = choices
            else:
                self.fields['application'].choices = [
                    ('', 'Nenhuma aplicação disponível')]
                self.fields['application'].disabled = True
        else:
            self.fields['application'].disabled = True
            self.initial['is_active'] = self.instance.application.is_active

    def save(self, commit=True):
        obj = super().save(commit=False)
        if getattr(obj, 'application', None):
            application = obj.application
            application.is_active = self.cleaned_data['is_active']
            if commit:
                application.save()
        if commit:
            obj.save()
        return obj
