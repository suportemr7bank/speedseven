"""
    Forms
"""
import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row
from django import forms
from pathvalidate import is_valid_filepath

from .models import EmailTemplate


def _remove_file(path):
    if os.path.exists(path):
        os.remove(path)
        folder = os.path.dirname(path)
        try:
            os.rmdir(folder)
        except OSError:
            pass


def remove_template(template: EmailTemplate):
    """
    Try to remove template.
    If file folder is empty, try to remove it.
    """
    #pylint: disable=no-member
    try:
        _remove_file(template.subject_path)
        _remove_file(template.message_path)

    except EmailTemplate.DoesNotExist:
        pass


class EmailTemplateForm(forms.ModelForm):
    """
    Save template text to file
    Remove file if it not related to any template record
    """

    subject_file = forms.CharField(
        label="Assunto", initial='-----', required=False)

    message_file = forms.CharField(
        label="Mensagem html", initial='-----', required=False)

    text_file = forms.CharField(
        label="Mensagem text", initial='-----', required=False)

    class Meta:
        """
        Meta data
        """
        model = EmailTemplate
        fields = '__all__'
        widgets = {
            'subject_tags': forms.Textarea(attrs={'rows': 3}),
            'message_tags': forms.Textarea(attrs={'rows': 6}),
            'text_template': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject_file'].widget.attrs['readonly'] = True
        self.fields['message_file'].widget.attrs['readonly'] = True
        self.fields['text_file'].widget.attrs['readonly'] = True

        if self.instance.pk:
            self._check_file('subject_file', self.instance.subject_path)
            self._check_file('message_file', self.instance.message_path)
            self._check_file('text_file', self.instance.text_path)

        self._set_layout()

    def _check_file(self, field, path):
        if os.path.isfile(path):
            self.initial[field] = path
        else:
            if self.instance.write_error:
                self.initial[field] = self.instance.write_error
            else:
                self.initial[field] = 'Arquivo não encontrato. Tente salvar novamente.'

    def _set_layout(self):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('prefix'),
                Column('type'),
            ),
            Row(
                Column('subject_file'),
                Column('message_file'),
                Column('text_file'),
            ),
            Row('subject_template'),
            Row('subject_tags'),
            Row('text_template'),
            Row('message_template'),
            Row('message_tags'),
        )

    def clean(self):
        cleaned_data = super().clean()
        path = cleaned_data['prefix']
        path = self._clean_path(path)

        if not is_valid_filepath(path):
            self.add_error('prefix', 'Prefixo inválido')

        cleaned_data['prefix'] = path

        return cleaned_data

    def _clean_path(self, path):
        path_cleaned = path
        if path_cleaned.startswith('/'):
            path_cleaned = path_cleaned.replace('/', '', 1)
        return path_cleaned

    def save(self, commit=True):
        if self.instance.pk:
            # pylint: disable=no-member
            old_template = EmailTemplate.objects.get(pk=self.instance.pk)
        else:
            old_template = None

        template = super().save(commit=False)
        if commit:
            if old_template:
                self._remove_old_file(old_template)
            self._save_template_field_to_file(template)
            template.save()
        return template

    def _save_template_field_to_file(self, template):
        """
        Save template text to file
        """
        subject_path, message_path, text_path = EmailTemplate.create_paths(
            template.prefix)

        try:
            # pylint: disable=broad-except
            os.makedirs(os.path.dirname(subject_path), exist_ok=True)
            template.write_error = ""
        except Exception:
            template.write_error = "Ocorreu um erro ao tentar criar diretório"
            return

        self._write_template(
            template, subject_path, template.subject_template, "Erro ao gravar assunto.")
        self._write_template(
            template, message_path, template.message_template, "Erro ao gravar mensagem (html).")
        self._write_template(
            template, text_path, template.text_template, "Erro ao gravar mensagem (txt)")

    def _write_template(self, template, path, text, error_message):
        try:
            with open(path, 'w', encoding="utf8") as file:
                file.write(text)
            template.write_error = ""
        except FileNotFoundError:
            template.write_error += error_message + ' '

    def _remove_old_file(self, template):
        remove_template(template)
