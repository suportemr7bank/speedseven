
"""
Core mixins

"""

from common.forms.mixins import FilterFormViewMixin

from. import filters


class OperationsFilterMixin(FilterFormViewMixin):
    """
    Filter client operation in reports
    """

    filter_form_class = filters.OperationsFilterForm

    def apply_filter(self, queryset, filter_form):
        """
        Apply filter to queryset
        """
        if filter_form.is_valid():
            product = filter_form.cleaned_data['product']
            if product:
                queryset = queryset.filter(
                    application_account__application__product__pk=product)

            operation = filter_form.cleaned_data['operation']
            if operation:
                queryset = queryset.filter(operation_type=operation)

        init_date = filter_form.cleaned_data['init_date']
        final_date = filter_form.cleaned_data['final_date']

        if init_date and final_date and init_date > final_date:
            filter_form.add_error(
                '', 'A data inicial deve ser menor que a final')

        if init_date:
            queryset = queryset.filter(operation_date__date__gte=init_date)

        if final_date:
            queryset = queryset.filter(operation_date__date__lte=final_date)

        return queryset
