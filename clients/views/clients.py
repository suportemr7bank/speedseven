"""
    Client views
"""


from constance import config
from django.db.models import F, Max, OuterRef, Subquery, Case, Value, When
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin

from accounts import roles as accounts_roles
from accounts import views as accounts_views
from accounts.auth import mixins as auth_mixins
from common.formats import decimal_format
from common.messages import message_modal_add
from common.views import generic, mixins

from core import models as core_models
from core import workflow
from investment import models as invest_models
from investment.views import application as invest_views, bank
from investment import tables as invest_tables
from investment.interfaces.enums import ApplicationFormType
from investorprofile import views as invprof_view
from products import models as products_models
from products.forms import mixins as products_forms_mixins
from products.forms import products as products_forms
from products.views import products as products_views


from clients.views.mixins import ClientRoleMixin, CompleteSignUpMixin

from .. import forms, models, tables


class StartView(CompleteSignUpMixin,
                mixins.TitleMixin,
                TemplateView):
    """
        Client start view
    """
    title = "Cadastro"
    header_message = 'Complete os passos abaixo'
    skip_signup_test = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_signup_completed:
            products_purchased, products_ids = self.get_products()
            if products_purchased:
                context['products'] = products_purchased
                purchase_id = self.request.GET.get(
                    'purchase_id', products_purchased[0]['purchase_id'])
                context['selected_product'] = purchase_id


            if products_ids:
                withdraw = []
                deposit = []
                widgets = []
                # pylint: disable=no-member
                query = invest_models.ApplicationAccount.objects.filter(
                    user=self.request.user, is_active=True)

                for app_acc in query:
                    application = app_acc.application
                    app_class = application.application_class
                    template = app_class.get_widget_template(
                        app_acc, self.request.theme)
                    if template:
                        widgets.append(
                            {
                                'name': app_acc.application.product.display_text,
                                'template': template
                            }
                        )
                    if app_class.get_form(ApplicationFormType.DEPOSIT, app_acc):
                        deposit.append(
                            {
                                'product': application.product.display_text,
                                'application_account_id': app_acc.pk
                            }
                        )
                    if app_class.get_form(ApplicationFormType.WITHDRAW, app_acc):
                        withdraw.append(
                            {
                                'product': application.product.display_text,
                                'application_account_id': app_acc.pk
                            }
                        )

                context['widgets'] = widgets
                context['operations'] = {
                    'deposit': deposit,
                    'withdraw': withdraw
                }

        net_balance = self._net_balance()
        total_balance = self._total_balance()
        context['net_balance'] = decimal_format(net_balance)
        context['blocked_balance'] = decimal_format(
            total_balance - net_balance)

        return context

    def _net_balance(self):
        #pylint: disable=no-member
        return invest_models.ApplicationAccount.total_income_balance(self.request.user)

    def _total_balance(self):
        #pylint: disable=no-member
        return invest_models.ApplicationAccount.total_balance(self.request.user)

    def get_products(self):
        """
        Return the user products
        """
        # pylint: disable=no-member
        user_products = products_models.ProductPurchase.objects.filter(
            application_account__is_active=True,
            user=self.request.user
        )

        products_ids = user_products.values('product__id').annotate(
            id=F('product__id')).values_list('id', flat=True).distinct()

        products_purchased = user_products.annotate(
            name=F('product__display_text'),
            purchase_id=F('pk'),
        ).values('name', 'purchase_id', 'product_id',
                 'application_account_id').order_by('purchase_id')

        return products_purchased, products_ids

    def get_template_names(self):
        if self.is_signup_completed:
            return ['clients/start/start.html']
        else:
            return ['clients/complete_signup.html']


class ClientUpdateView(CompleteSignUpMixin,
                       workflow.ApprovalWorkflowViewMixin,
                       generic.UpdateView):
    """
        Update client
        Client is created by signal when user signed up
    """
    model = models.Client
    form_class = forms.ClientForm
    template_name = 'common/form.html'
    title = 'Dados pessoais'
    success_url = reverse_lazy('clients:start_page')
    cancel_url = success_url
    skip_signup_test = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['operator'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        # pylint: disable=no-member
        try:
            return self.model.objects.get(user=self.request.user)
        except self.model.DoesNotExist:
            return None


class BankAccountListView(CompleteSignUpMixin,
                          bank.BankAccountBaseListView):
    """
    Client bank account list
    """

    table_class = invest_tables.bank_account_table(
        'clients:bank_account_update')
    skip_signup_test = True

    controls = [
        {'link': {'text': 'Novo', 'url': 'clients:bank_account_create'}},
    ]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_list.count() >= config.MAX_BANK_ACCOUNT_NUMBER:
            context['controls'] = None
        return context


class BankAccountCreateView(CompleteSignUpMixin,
                            bank.BankAccountCreateView):
    """
    Client bank account create
    """

    success_url = reverse_lazy('clients:bank_account_list')
    cancel_url = success_url
    skip_signup_test = True


class BankAccountUpdateView(CompleteSignUpMixin,
                            bank.BankAccountUpdateView):
    """
    Client bank account update
    """

    success_url = reverse_lazy('clients:bank_account_list')
    cancel_url = success_url
    skip_signup_test = True


class ProductsView(CompleteSignUpMixin,
                   mixins.TitleMixin,
                   TemplateView):
    """
    Client products view
    """
    title = 'Produtos'
    template_name = 'clients/products/products.html'

    def _get_products(self):
        # pylint: disable=no-member

        user = self.request.user
        user_products = Subquery(products_models.Product.objects.filter(
            productpurchase__user=user).values('pk'))

        products = products_models.Product.objects.filter(
            application__is_active=True,
        ).annotate(
            agreement_id=Max('agreementtemplate__pk'),
            purchased=Case(When(pk__in=user_products, then=Value(True)))
        )

        for product in products:
            product.application_info = product.application.application_class.get_application_info(
                product.application, self.request.theme)

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self._get_products()
        context['categories'] = products_models.Product.group_by_category(
            products)
        context['products'] = products
        bank_account = self.request.user.bankaccount_set.filter(
            main_account=True).first()
        context['banck_account'] = bank_account
        return context


class ProductsPurchaseView(ProductsView):
    """
    Client products view
    """
    title = 'Contratar produto'
    template_name = 'clients/products/purchase.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['products'].get(pk=kwargs['pk'])

        # get removes application_info
        product.application_info = product.application.application_class.get_application_info(
            product.application, self.request.theme)

        context['product'] = product
        if investor_profile := self.request.user.investorprofile_set.last():
            context['product_access'] = product.profileproduct_set.filter(
                profile=investor_profile.profile).exists()

        application_class = product.application.application_class
        purchase_form = application_class.get_form(
            ApplicationFormType.APPLICATION_PURCHASE)
        if not purchase_form:
            purchase_form = products_forms.PurchaseForm

        if self.request.method == 'GET':
            context['purchase_form'] = purchase_form(
                product=product, user=self.request.user)
        else:
            context['purchase_form'] = purchase_form(
                self.request.POST, product=product, user=self.request.user)
        return context

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        """
        Request remote product creation and create a local respective product
        """
        context = self.get_context_data(**kwargs)

        if context['product']:
            form = context['purchase_form']
            if form.is_valid():
                form.save()
                message_modal_add(request, context, 'Parabéns!',
                                  'Investimento contratado com sucesso!')
                return redirect(reverse('clients:start_page'))
        else:
            form.add_error(
                None, 'Contratação indisponível no momento')

        return self.render_to_response(context)


class BrokerView(CompleteSignUpMixin,
                 mixins.TitleMixin,
                 TemplateView):
    """
        Client broker view
    """
    title = "Broker"
    header_message = ''

    template_name = 'clients/broker/broker.html'


class OperationsStatentView(
        CompleteSignUpMixin,
        products_forms_mixins.OperationsFilterMixin,
        mixins.TitleMixin,
        SingleTableMixin,
        TemplateView):
    """
        Client report  view
    """
    title = 'Extrato de movimentação'
    header_message = ''
    template_name = 'clients/reports/operations_statement.html'
    table_class = tables.ReportTable


class ReportView(
        CompleteSignUpMixin,
        mixins.TitleMixin,
        TemplateView):
    """
        Client report  view
    """
    title = 'Relatório'
    header_message = ''
    template_name = 'clients/reports/report.html'


class ProductPurcahseListView(CompleteSignUpMixin,
                              mixins.ListViewMixin):
    """
    Agreements list
    """
    model = products_models.ProductPurchase
    table_class = tables.ProductPurchaseTable
    template_name = 'common/list.html'
    title = 'Investimentos'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class ProductPurchaseUpdateView(CompleteSignUpMixin,
                                generic.UpdateView):
    """
    Update product
    """

    model = products_models.ProductPurchase
    fields = "__all__"
    template_name = 'common/form.html'
    fields = ['auto_renew', 'notify_before_end']
    title = 'Investimento'
    success_url = reverse_lazy('clients:products_purchase_list')
    cancel_url = success_url

    def get_object(self, queryset=None):
        # pylint: disable=no-member
        pp_pk = self.kwargs.get('pk')
        try:
            return self.model.objects.get(pk=pp_pk, user=self.request.user)
        except self.model.DoesNotExist as exc:
            raise Http404(exc) from exc

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if days := getattr(config, 'AGREEMENT_NOTIFY_END_BEFORE_DAYS', 15):
            form.fields[
                'notify_before_end'].label = f"Notificar término do contrato {days} antes do vencimento"
        return form


class UserAcceptanceTermListView(CompleteSignUpMixin,
                                 mixins.ListViewMixin):
    """
    Acceptance terms list
    """
    permission_required = 'is_admin'
    model = core_models.AcceptanceTerm
    table_class = tables.AcceptanceTable
    template_name = 'common/list.html'
    title = 'Termos de aceite'

    def get_queryset(self):
        # pylint: disable=no-member
        last_vertions = core_models.AcceptanceTerm.objects.filter(
            is_active=True, type=OuterRef('type')).order_by('-version')
        # pylint: disable=no-member
        last_vertions = core_models.AcceptanceTerm.objects.filter(
            pk=Subquery(last_vertions.values('pk')[:1]))
        return last_vertions


class UserAcceptanceTermPrintView(CompleteSignUpMixin,
                                  generic.PrintView):
    """
    Detail and print view for acceptance terms
    """

    model = core_models.AcceptanceTerm
    template_name = 'common/print.html'
    title = 'Termo de aceite'

    def get_content(self):
        accept_term_pk = self.kwargs.get('pk', None)
        if accept_term_pk:
            try:
                # pylint: disable=no-member
                term = core_models.AcceptanceTerm.objects.get(
                    pk=accept_term_pk,
                )
                return {
                    'title': term.title,
                    'text': term.text
                }
            # pylint: disable=no-member
            except core_models.AcceptanceTerm.DoesNotExist as exc:
                raise Http404(exc) from exc

        return dict()


class UserAcceptanceTermCreateView(ClientRoleMixin,
                                   mixins.PageMenuMixin,
                                   generic.FormView):
    """
    View to accept terms
    """

    menu_template_name = 'clients/menu.html'
    template_name = 'common/term_form.html'
    form_class = forms.UserAcceptanceTermForm
    title = 'Termo de aceite'
    header_message = ''
    success_url = reverse_lazy('clients:start_page')

    def __init__(self) -> None:
        super().__init__()
        # pylint: disable=no-member
        self.term = core_models.AcceptanceTerm.objects.filter(
            type=core_models.AcceptanceTerm.Type.PRIVACY_POLICY, is_active=True).order_by('-version').last()

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['term'] = self.term
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.term:
            context['term'] = {
                'title': self.term.title,
                'text': self.term.text
            }
        return context

    def get_controls(self):
        """
        No controls required
        """
        return [mixins.Control('button', 'button', 'accept', 'Aceitar', 'success')]


class InvestorProfileTestCreateView(ClientRoleMixin,
                                    invprof_view.ProfileTestCreateViewMixin,
                                    mixins.PageMenuMixin,
                                    generic.FormView):
    """
    Investor profile test view
    """
    menu_template_name = 'clients/menu.html'
    template_name = 'investorprofile/form.html'
    title = 'Perfil de investidor'
    header_message = ''
    success_url = reverse_lazy('clients:start_page')


class InvestorProfileTestUpdateView(CompleteSignUpMixin,
                                    invprof_view.ProfileTestBaseViewMixin,
                                    mixins.PageMenuMixin,
                                    generic.FormView):
    """
    Investor profile test view
    """
    menu_template_name = 'clients/menu.html'
    template_name = 'investorprofile/form.html'
    title = 'Refazer teste'
    header_message = '<h4 class="text-success">Atenção! Ao refazer o teste seu perfil será recalculado!</h4>'
    success_url = reverse_lazy('clients:investor_profile_test_detail')
    cancel_url = success_url

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        investor_profile = self.request.user.investorprofile_set.last()
        form_kwargs['instance'] = investor_profile
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enable_confirm'] = True
        return context

    def get_controls(self):
        controls = super().get_controls()
        for control in controls:
            if control.value == 'save':
                control.disabled = True
        return controls

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        message_modal_add(request, context, 'Parabéns!',
                          'Seu perfil foi recalculado com sucesso')
        return response


class InvestorProfileTestDetailView(CompleteSignUpMixin,
                                    invprof_view.ProfileTestBaseViewMixin,
                                    mixins.PageMenuMixin,
                                    generic.FormView):
    """
    Investor profile test view
    """
    menu_template_name = 'clients/menu.html'
    template_name = 'investorprofile/form.html'
    title = 'Perfil de investidor'
    cancel_url = reverse_lazy('clients:start_page')

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        investor_profile = self.request.user.investorprofile_set.last()
        context['instance'] = investor_profile
        if investor_profile:
            self.header_message = f'<h2 class="text-danger">{investor_profile.profile.display_text}</h1>'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for key, field in form.fields.items():
            field.disabled = True
        return form

    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=['GET'], content='Method not allowed')

    def get_controls(self):
        return [
            mixins.ControlFactory.cancel_button(redirect_url=self.cancel_url),
            mixins.ControlFactory.link_button(label='Refazer teste', url=reverse(
                'clients:investor_profile_test_update'), color='success')
        ]


class UserAgreementPrintView(CompleteSignUpMixin,
                             generic.PrintView):
    """
    Detail and print view for acceptance terms
    """

    model = products_models.ProductPurchase
    template_name = 'common/print.html'
    title = 'Contrato'

    def get_content(self):
        product_pk = self.kwargs.get('pk', None)
        if product_pk:
            try:
                # pylint: disable=no-member
                user_agreement = self.model.objects.get(
                    pk=product_pk,
                    user=self.request.user
                )
                return {
                    'text': user_agreement.agreement
                }
                # pylint: disable=no-member
            except self.model.DoesNotExist as exc:
                raise Http404(exc) from exc

        return dict()


class SignupView(accounts_views.SignupView):
    """
    Signup view adpted to client

    If the role set in invitation is CLIENT, presents a modal for
    signup terms acceptance.
    If acceptance_required is true, a term must be given
    """

    def get_term(self):
        # pylint: disable=no-member
        email = self.request.session.get("account_verified_email", None)
        invitation = accounts_roles.has_active_invitation(email)
        if invitation:
            role = accounts_roles.get_role_from_invitation_email(email)
            if role == accounts_roles.Roles.CLIENT:
                self.acceptance_required = True
                term = core_models.AcceptanceTerm.objects.filter(
                    type=core_models.AcceptanceTerm.Type.SIGNUP, is_active=True).order_by('-version').last()
                if term:
                    return {
                        'title': term.title,
                        'text': term.text
                    }
            else:
                self.acceptance_required = False
        else:
            self.acceptance_required = True
            term = core_models.AcceptanceTerm.objects.filter(
                type=core_models.AcceptanceTerm.Type.SIGNUP, is_active=True).order_by('-version').last()
            if term:
                return {
                    'title': term.title,
                    'text': term.text
                }
        return None


class ClientDocsView(auth_mixins.LoginRequiredMixin, generic.FileBaseView):
    """
    View to download client uploaded documents
    Client can view/download only its documents
    Users with ADMIN role has access to all documents
    """

    model = models.Client
    field = 'rg_cnh'
    media_file_root = 'private/uploads/'

    def can_access_file(self, request):
        user = request.user
        roles = [accounts_roles.Roles.ADMIN, accounts_roles.Roles.CLIENT]
        if accounts_roles.has_role_in(user, roles):
            return True
        return False

    def queryset(self, file_name, request):

        field_prefix = file_name.split('/')[-1].split('_')[0]

        if field_prefix == 'rc':
            self.field = 'rg_cnh'
        elif field_prefix == 'ap':
            self.field = 'address_proof'
        elif field_prefix == 'ca':
            self.field = 'company_agreement'
        else:
            # pylint: disable=no-member
            return self.model.objects.none()

        data = {
            f'{self.field}__exact': f'{self.media_file_root}{file_name}',
        }

        # pylint: disable=no-member
        query = self.model.objects.filter(**data)

        user = request.user

        if accounts_roles.has_role(user, accounts_roles.Roles.ADMIN):
            return query
        elif accounts_roles.has_role(user, accounts_roles.Roles.CLIENT):
            return query.filter(user=user)
        return query.none()


class ApplicationOpUserListView(CompleteSignUpMixin,
                                products_forms_mixins.OperationsFilterMixin,
                                invest_views.ApplicationOpUserListBaseView):
    """
    Client application operation list view
    """

    def get_queryset(self):
        return super().get_queryset().filter(application_account__user=self.request.user)


class HelpView(CompleteSignUpMixin, TemplateView):
    """
    Help view
    """
    menu_template_name = 'clients/menu.html'
    skip_signup_test = True
    template_name = 'clients/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pylint: disable=no-member
        context['company'] = core_models.Company.objects.last()
        context['faq'] = core_models.FAQConfig.get_faq(target_page=core_models.FAQConfig.Page.CLIENT)
        return context


class CategoryDocumentDetailView(CompleteSignUpMixin,
                                 products_views.CategoryDocumentDetailView):
    """
    Client category document detail view
    """
