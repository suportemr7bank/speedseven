"""
    Product views
"""


from django.http import JsonResponse
from django.urls import reverse_lazy
from django import views as django_view

from accounts.auth import mixins as auth_mixins
from common.views import generic, mixins

from investorprofile import models as invprov_models

from .. import tables
from .. import models
from .. import forms


class ProductListView(mixins.AdminMixin,
                      mixins.ListViewMixin):
    """
    Products list
    """
    model = models.Product
    table_class = tables.ProductTable
    template_name = 'common/list.html'
    title = 'Produto'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:product_create'}},
    ]


class ProductCreateView(mixins.AdminMixin,
                        generic.CreateView):
    """
    Create product
    """
    model = models.Product
    form_class = forms.products.ProductForm
    template_name = 'common/form.html'
    title = 'Produto'
    success_url = reverse_lazy('products:product_list')
    cancel_url = success_url


class ProductUpdateView(mixins.AdminMixin,
                        generic.UpdateView):
    """
    Update product
    """
    model = models.Product
    form_class = forms.products.ProductForm
    template_name = 'common/form.html'
    title = 'Produto'
    success_url = reverse_lazy('products:product_list')
    cancel_url = success_url


class ProductPurchaseListView(mixins.AdminMixin,
                              mixins.ListViewMixin):
    """
    Products list
    """
    model = models.ProductPurchase
    table_class = tables.ProductPurchaseTable
    template_name = 'common/list.html'
    title = 'Produtos contratados'


class ProductJsonData(auth_mixins.LoginRequiredMixin, django_view.View):
    """
    Agreement text for aggrement modals
    """

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        Agreement data
        """
        product_pk = self.request.GET.get('id', None)
        if product_pk:
            try:
                #pylint: disable=no-member
                product = models.Product.objects.get(pk=product_pk)
            except models.Product.DoesNotExist:
                return JsonResponse({"error": 'Produto não encontrado'}, status=400)

            if product:
                return JsonResponse({
                    'title': 'Informações do produto',
                    'text': product.info,
                    'product_name': product.display_text
                },
                    status=200)
        return JsonResponse({"error": 'Sem informaçõe adicionais'}, status=400)


class DashboardListView(mixins.AdminMixin,
                        mixins.ListViewMixin):
    """
    Dashboards list
    """
    model = models.Dashboard
    table_class = tables.DashboardTable
    template_name = 'common/list.html'
    title = 'Dashboard'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:dashboard_create'}},
    ]


class DashboardCreateView(mixins.AdminMixin,
                          generic.CreateWitthInlinesView):
    """
    Create dashboard
    """
    model = models.Dashboard
    fields = "__all__"
    inlines = [forms.products.DashboardProductItem]
    template_name = 'common/formset.html'
    title = 'Dashboard'
    success_url = reverse_lazy('products:dashboard_list')
    cancel_url = success_url


class DashboardUpdateView(mixins.AdminMixin,
                          generic.UpdateWitthInlinesView):
    """
    Update dashboard
    """
    model = models.Dashboard
    fields = "__all__"
    inlines = [forms.products.DashboardProductItem]
    template_name = 'common/formset.html'
    title = 'Dashboard'
    success_url = reverse_lazy('products:dashboard_list')
    cancel_url = success_url


class ProfileProductListView(mixins.AdminMixin,
                             mixins.ListViewMixin):
    """
    Products profile list
    """
    model = invprov_models.Profile
    table_class = tables.ProfileProductTable
    template_name = 'common/list.html'
    title = 'Produtos do perfil'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:profile_product_create'}},
    ]


class ProfileProductCreate(mixins.AdminMixin,
                           generic.CreateWitthInlinesView):

    """
    Profile product create
    """
    model = invprov_models.Profile
    fields = ['name', 'display_text']
    inlines = [forms.products.ProfileProductItem]
    template_name = 'common/formset.html'
    title = 'Perfil'
    success_url = reverse_lazy('products:profile_product_list')
    cancel_url = success_url


class ProfileProductUpdate(mixins.AdminMixin,
                           generic.UpdateWitthInlinesView):

    """
    Profile product create
    """
    permission_required = 'is_admin'
    model = invprov_models.Profile
    fields = ['name', 'display_text']
    inlines = [forms.products.ProfileProductItem]
    template_name = 'common/formset.html'
    title = 'Perfil'
    success_url = reverse_lazy('products:profile_product_list')
    cancel_url = success_url


class ProductCategoryListView(mixins.AdminMixin,
                              mixins.ListViewMixin):
    """
    Product category list
    """
    model = models.ProductCategory
    table_class = tables.ProductCategoryTable
    template_name = 'common/list.html'
    title = 'Categoria'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:category_create'}},
    ]


class ProductCategoryCreateView(mixins.AdminMixin,
                                generic.CreateView):
    """
    Create product category
    """
    model = models.ProductCategory
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Categoria'
    success_url = reverse_lazy('products:category_list')
    cancel_url = success_url


class ProductCategoryUpdateView(mixins.AdminMixin,
                                generic.UpdateView):
    """
    Update product category
    """
    model = models.ProductCategory
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Categoria'
    success_url = reverse_lazy('products:category_list')
    cancel_url = success_url


class CategoryDocumentListView(mixins.AdminMixin,
                               mixins.ListViewMixin):
    """
    Category document list
    """
    model = models.CategoryDocument
    table_class = tables.CategoryDocumentTable
    template_name = 'common/list.html'
    title = 'Documentos das categorias'
    controls = [
        {'link': {'text': 'Novo', 'url': 'products:category_document_create'}},
    ]


class CategoryDocumentCreateView(mixins.AdminMixin,
                                 generic.CreateView):
    """
    Create category document
    """
    model = models.CategoryDocument
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Documento da categoria'
    success_url = reverse_lazy('products:category_document_list')
    cancel_url = success_url


class CategoryDocumentUpdateView(mixins.AdminMixin,
                                 generic.UpdateView):
    """
    Update category document
    """
    model = models.CategoryDocument
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Documento da categoria'
    success_url = reverse_lazy('products:category_document_list')
    cancel_url = success_url


class CategoryDocumentDetailView(generic.PrintView):
    """
    Detail category document
    """
    model = models.CategoryDocument
    template_name = 'common/print.html'

    def get_context_data(self, **kwargs):
        self.title = self.object.category.title
        return super().get_context_data(**kwargs)

    def get_content(self):
        return {'title': self.object.display_text, 'text': self.object.text}
