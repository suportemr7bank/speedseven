"""
    Agreement views
"""
from http import HTTPStatus

from django.http import Http404, JsonResponse
from django.urls import reverse_lazy
from django.views import View

from accounts.auth import mixins as auth_mixins
from common.views import generic, mixins
from products import models as product_models

from .. import tables
from ..forms.products import AgreementForm
from ..models import AgreementTemplate


class AgreementListView(mixins.AdminMixin,
                        mixins.ListViewMixin):
    """
    Agreements list
    """
    model = AgreementTemplate
    table_class = tables.AgreementTable
    template_name = 'common/list.html'
    title = 'Modelos de contrato'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:agreement_create'}},
    ]


class AgreementCreateView(mixins.AdminMixin,
                          generic.CreateView):
    """
    Create agreement
    """
    model = AgreementTemplate
    form_class = AgreementForm
    template_name = 'common/form.html'
    title = 'Modelo de contrato'
    success_url = reverse_lazy('products:agreement_list')
    cancel_url = success_url


class AgreementUpdateView(mixins.AdminMixin,
                          generic.UpdateView):
    """
    Update agreement
    """
    model = AgreementTemplate
    form_class = AgreementForm
    template_name = 'common/form.html'
    title = 'Modelo de contrato'
    success_url = reverse_lazy('products:agreement_list')
    cancel_url = success_url


class AgreementJsonView(auth_mixins.LoginRequiredMixin, View):
    """
    Product agreeemnt text
    """

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        Product agreement text
        """
        product_id = self.request.GET.get('product_id')

        if product_id:
            # pylint: disable=no-member
            agreement_template = AgreementTemplate.objects.filter(
                product__pk=product_id,
                type=self.request.user.client.type).last()

            agreement_renderer = agreement_template.product.application. \
                application_class.get_agreement_class()

            if agreement_template:
                text = agreement_renderer.render(
                    self.request.user, agreement_template.text, extra_args=self.request.GET)
                return JsonResponse(
                    {
                        "text": text,
                        'agreement_term': agreement_template.term_str,
                        'product': {
                            'display_text': agreement_template.product.display_text

                        }

                    }, status=HTTPStatus.OK)

        return JsonResponse(
            {"error": 'Contrato indisponível no momento'},
            status=HTTPStatus.OK
        )


class UserAgreementPrintView(mixins.AdminMixin,
                             generic.PrintView):
    """
    Detail and print view for acceptance terms
    """

    model = product_models.ProductPurchase
    template_name = 'common/print.html'
    title = 'Contrato do cliente'

    def get_content(self):
        product_purchase_pk = self.kwargs.get('pk', None)
        if product_purchase_pk:
            try:
                # pylint: disable=no-member
                user_agreement = self.model.objects.get(
                    pk=product_purchase_pk,
                )
                return {
                    'text': user_agreement.agreement
                }
                # pylint: disable=no-member
            except self.model.DoesNotExist as exc:
                raise Http404(exc) from exc
        return dict()


class UserAgreementPreview(mixins.AdminMixin,
                           generic.PrintView):
    """
    Detail and print view for acceptance terms
    """

    model = product_models.AgreementTemplate
    template_name = 'common/print.html'
    title = 'Exemplo de contrato'

    def get_content(self):
        agreement_pk = self.kwargs.get('pk', None)
        if agreement_pk:
            try:
                # pylint: disable=no-member
                agreement = self.model.objects.get(
                    pk=agreement_pk,
                )

                agreement_renderer = agreement.product.application.application_class.get_agreement_class()

                text = '<h5>Exemplo de contrato para visualização</h5><br>'+agreement.text
                return {
                    'text': agreement_renderer.render(
                        user=None, agreement_text=text, preview=True)
                }
                # pylint: disable=no-member
            except self.model.DoesNotExist as exc:
                raise Http404(exc) from exc
        return dict()
