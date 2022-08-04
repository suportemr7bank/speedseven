"""
Webite public views
"""

from django.views.generic import TemplateView, DetailView

from core.models import Company, FAQConfig, AcceptanceTerm
from products.models import Product
from products.views import products as producs_views


class ProducsMixin:
    """
    Add products in the template context
    """

    def get_context_data(self, **kwargs):
        """
        Add products to context
        """
        context = super().get_context_data(**kwargs)
        # pylint: disable=no-member

        products = Product.objects.filter(application__is_active=True)

        for product in products:
            product.application_info = product.application.application_class.get_application_info(
                product.application, self.request.theme)

        context['products'] = products

        context['categories'] = Product.group_by_category(products)

        if company := Company.objects.all().last():
            context['company'] = company
        return context


class LandingView(ProducsMixin, TemplateView):
    """
    Site landing page
    """
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq'] = FAQConfig.get_faq(target_page=FAQConfig.Page.PUBLIC)
        return context


class ProductsView(ProducsMixin, TemplateView):
    """
    Site landing page
    """
    template_name = 'website/products.html'


class CategoryDocumentDetailView(producs_views.CategoryDocumentDetailView):
    """
    Detail category document
    """
    template_name = 'website/category_docs.html'


class AcceptanceTermPrintView(DetailView):
    """
    Detail and print view for acceptance terms
    """

    model = AcceptanceTerm
    template_name = 'website/terms.html'

    def get_object(self, queryset=None):
        accept_term_type = self.kwargs.get('type', None)
        if accept_term_type:

            if accept_term_type == 'termo-de-uso':
                accept_term_type = 'SIG'
            elif accept_term_type == 'politica-de-privacidade':
                accept_term_type = 'PPO'
            else:
                return None

            # pylint: disable=no-member
            term = AcceptanceTerm.objects.filter(
                type=accept_term_type,
            ).last()
            return term

        return None
