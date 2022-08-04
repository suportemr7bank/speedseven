"""
Start page form
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, HTML
from crispy_forms.bootstrap import PrependedText
from django import forms
from django.contrib.sites.models import Site

from core import models


class StartPageForm(forms.ModelForm):
    """
    Star page form
    """

    site_name = forms.CharField(max_length=50, label='Nome do site')

    class Meta:
        """
        Meta class
        """
        model = models.Company
        fields = [
            'site_name', 'contact_email', 'support_email', 'support_phone',
            'about_us', 'logo', 'name_logo', 'abt_us_signup_btn',
            'abt_us_bkg_color', 'disclaimer', 'fix_disclaimer_end',
            'facebook_link', 'linkedin_link', 'instagram_link'
        ]
        widgets = {
            'disclaimer': forms.widgets.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site = None
        if self.instance.pk:
            self.site = Site.objects.get_current()
            self.initial['site_name'] = self.site.name

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('site_name'), Column('support_phone'), Column(HTML(''))),
            Row(Column('logo'), Column('name_logo'), Column(HTML(''))),
            Row(Column('contact_email'), Column(
                'support_email'), Column(HTML(''))),
            Row(HTML('<hr>'), css_class='my-2'),
            Row(Column('about_us')),
            Row(Column('abt_us_signup_btn'), Column('abt_us_bkg_color')),
            Row(HTML('<hr>'), css_class='my-2'),
            Row(Column(PrependedText('facebook_link', 'https://facebook.com/', css_class='border-start border-secondary')),
                Column(HTML('')), Column(HTML(''))),
            Row(Column(PrependedText('linkedin_link', 'https://linkedin.com/', css_class='border-start border-secondary')),
                Column(HTML('')), Column(HTML(''))),
            Row(Column(PrependedText('instagram_link', 'https://instagram.com/', css_class='border-start border-secondary')),
                Column(HTML('')), Column(HTML(''))),
            Row(HTML('<hr>'), css_class='my-2'),
            Row(Column('disclaimer')),
            Row(Column('fix_disclaimer_end')),
        )

    def save(self, commit=True):
        """
        Save site name
        """
        obj = super().save(commit)
        if self.site and 'site_name' in self.changed_data:
            self.site.name = self.cleaned_data['site_name']
            if commit:
                self.site.save()
        if commit:
            obj.save()
        return obj
