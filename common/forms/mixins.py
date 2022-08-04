"""
Filter form mixin
"""

from django.db.models import Q

from . import filters


class FilterFormViewMixin:
    """
    Class to create filter form for listview
    """

    filter_form_class = None

    def get_context_data(self, **kwargs):
        """
        Insert filter form in the context
        """
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['filter_form'] = self.filter_form
        return context

    def get_queryset(self):
        """
        Get queryset to apply filter
        """
        queryset = super().get_queryset()
        try:
            user = self.request.user

            # pylint: disable=not-callable
            if self.request.GET:
                self.filter_form = self.filter_form_class(
                    self.request.GET, user=user)
            else:
                self.filter_form = self.filter_form_class(user=user)
            if self.filter_form.is_valid():
                return self.apply_filter(queryset, self.filter_form)
            else:
                return queryset
        except AttributeError:
            self.filter_form = None
            return queryset.none()

    # pylint: disable=unused-argument
    def apply_filter(self, queryset, filter_form):
        """
        Apply filter to queryset
        """
        return queryset


class NameEmailFilterMixin(FilterFormViewMixin):
    """
    Name and email fields filter
    """
    filter_form_class = filters.NameEmailFilterForm

    def apply_filter(self, queryset, filter_form):
        value = filter_form.cleaned_data.get('value')
        if value:
            field_name = filter_form.cleaned_data.get('field_name')
            if field_name == 'name':
                return self.name_query(queryset, value)
            elif field_name == 'email':
                return self.email_query(queryset, value)
        return queryset

    # pylint: disable=unused-argument
    def name_query(self, queryset, name):
        """
        Filter query by name
        Default imlementation does nothing
        """
        return queryset

    # pylint: disable=unused-argument
    def email_query(self, queryset, email):
        """
        Filter query by email
        Default imlementation does nothing
        """
        return queryset


class UserNameEmailFilterMixin(NameEmailFilterMixin):
    """
    Filter for User model
    """

    model_user_field = None

    def name_query(self, queryset, name):
        first_name_query = 'first_name__icontains'
        last_name_query = 'last_name__icontains'
        if self.model_user_field:
            first_name_query = self.model_user_field +'__'+first_name_query
            last_name_query = self.model_user_field +'__'+last_name_query

        name_list = name.split()
        query = Q()
        for word in name_list:
            query |= Q(**{first_name_query: word}) | Q(
                **{last_name_query:word})
        return queryset.filter(query)

    def email_query(self, queryset, email):
        email_query = 'email__icontains'
        if self.model_user_field:
            email_query = self.model_user_field +'__'+email_query
        return queryset.filter(**{email_query: email})


class EmailFilterMixin(NameEmailFilterMixin):
    """
    Name and email fields filter
    """
    filter_form_class = filters.EmailFilterForm

    def apply_filter(self, queryset, filter_form):
        value = filter_form.cleaned_data.get('value')
        if value:
            field_name = filter_form.cleaned_data.get('field_name')
            if field_name == 'email':
                return self.email_query(queryset, value)
        return queryset

    # pylint: disable=unused-argument
    def email_query(self, queryset, email):
        """
        Filter query by email
        Default imlementation does nothing
        """
        return queryset


class InvitationEmailFilterMixin(EmailFilterMixin):
    """
    Filter for User model
    """

    def email_query(self, queryset, email):
        return queryset.filter(email__icontains=email)


class LoggedUserMixin:
    """
    Insert logged user in the from kwargs
    """

    def get_form_kwargs(self):
        """
        Insert logged user in the from kwargs
        """
        kwargs = super().get_form_kwargs()
        #pylint: disable=no-member
        kwargs['user'] = self.request.user
        return kwargs
