"""
Base models for workflow
"""

from crispy_forms.layout import HTML, Column, Layout, Row
from django.db import models
from django.utils import timezone
from django.conf import settings

from common.views.mixins import ControlFactory
from core.models import WorkflowTask


class ApprovalWorkflow(models.Model):
    """
    Base fields used by register approval
    """

    class Meta:
        """
        Meta class
        """
        abstract = True

    initial_status_created = False
    task_name = None
    form_view = None
    exclude_fields = []

    class Status(models.TextChoices):
        """
        Approval operation status
        """
        CREATED = 'CRE', "Criado"
        WAITING = 'WAI', "Aguardando"
        APPROVED = 'APP', "Aprovado"
        DISAPROVED = 'DIS', "Reprovado"

    message = models.CharField(
        verbose_name='Mensagem', max_length=2048, null=True, blank=True)

    status = models.CharField(verbose_name='Situação', max_length=3,
                              choices=Status.choices, null=True, blank=True)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Operador',
                                 on_delete=models.CASCADE,  related_name="+", editable=False)

    @property
    def approved(self):
        """
        Return if register is approved
        """
        return self.status == ApprovalWorkflow.Status.APPROVED

    @property
    def disapproved(self):
        """
        Return if register is disapproved
        """
        return self.status == ApprovalWorkflow.Status.DISAPROVED

    @property
    def created(self):
        """
        Return if register is created
        """
        return self.status == ApprovalWorkflow.Status.CREATED

    @property
    def waiting(self):
        """
        Return if register is waiting approval
        """
        return self.status == ApprovalWorkflow.Status.WAITING

    # pylint: disable=no-member

    def save(self, *args, **kwargs) -> None:
        """
        Intercept save to create a task
        """

        if self.pk is None:
            if self.initial_status_created:
                self.status = ApprovalWorkflow.Status.CREATED
        else:
            if not self._record_changed():
                super().save(*args, **kwargs)
                return None

        if not self.status:
            self.status = ApprovalWorkflow.Status.CREATED
            super().save(*args, **kwargs)

        elif self.status == ApprovalWorkflow.Status.CREATED:

            self._save_and_create_task(args, kwargs)

        elif self.status in [ApprovalWorkflow.Status.APPROVED, ApprovalWorkflow.Status.DISAPROVED]:

            task = WorkflowTask.objects.filter(register_id=self.id).last()
            if not task.verified:
                curr_date = timezone.localtime(timezone.now())
                date = curr_date.strftime('%d/%m/%Y %H:%M:%S')
                if self.status == ApprovalWorkflow.Status.APPROVED:
                    self.message = f'Última atualização realizada em {date}'
                super().save(*args, **kwargs)
                self._complete_task(task, curr_date)
            else:
                self._save_and_create_task(args, kwargs)

    def _save_and_create_task(self, args, kwargs):
        self.status = ApprovalWorkflow.Status.WAITING
        super().save(*args, **kwargs)
        self._create_task()

    def _complete_task(self, task, curr_date):
        task.evaluator = self.operator
        task.date_verified = curr_date
        task.status = self.get_status_display()
        task.save()

    def _create_task(self):
        history_id = self.history.filter(id=self.id).first().history_id
        model = self.history.model
        history_model = f'{model.__module__}.{model.__name__}'
        WorkflowTask.objects.create(
            history_id=history_id,
            name=self.task_name,
            operator=self.operator,
            register_id=self.id,
            form_view=self.form_view,
            history_model=history_model,
            status=self.get_status_display()
        )

    def _record_changed(self):
        """
        Verify if some field not in excluded fields has changed.
        It allows exclude_fields modification without creating a workflow approval task
        """
        exclude_fields = self.exclude_fields + ['operator']
        if self.pk is not None and self.exclude_fields is not None:
            orig = self._meta.model.objects.get(pk=self.pk)
            field_names = [field.name for field in self._meta.fields if field.name not in exclude_fields]
            for field_name in field_names:
                changed = getattr(orig, field_name) != getattr(self, field_name)
                if changed:
                    return True
        return False


class ApprovalWorkflowFormMixin:
    """
    Approval form configuration
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_workflow()

    def _init_workflow(self):
        status = ApprovalWorkflow.Status
        choices = [
            ('', '-----'),
            (status.APPROVED.value, status.APPROVED.label),
            (status.DISAPROVED.value, status.DISAPROVED.label),
        ]

        self.fields.pop('operator', None)

        self.fields['status'].choices = choices
        self.fields['status'].required = True

        if self.instance.status == status.WAITING:
            for _key, field in self.fields.items():
                field.disabled = True
            if self.operator.is_superuser:
                self.fields['status'].disabled = False
                self.fields['message'].disabled = False

        elif self.instance.status in [status.DISAPROVED, status.APPROVED]:
            self.fields['status'].disabled = True
            self.fields['message'].disabled = True

        elif self.instance.status in [None, status.CREATED]:
            self.fields.pop('status')
            self.fields.pop('message')

        if not self.operator.is_superuser:
            self.fields.pop('status', None)

    @property
    def workflow_layout(self):
        """
        Set layout
        """
        status = ApprovalWorkflow.Status
        layout = Layout()
        if self.instance.status == status.WAITING:
            layout.insert(
                0,
                Row(Column(
                    HTML('<p class="h6 pt-2 text-success">Aguardando aprovação</p>')))
            )

            if self.operator.is_superuser:
                layout.insert(1, Row(Column('status')))
                layout.insert(2, Row(Column('message')))

        elif self.instance.status == status.DISAPROVED:
            layout.insert(
                0,
                Row(Column(
                    HTML('<p class="h6 pt-2 text-success">Faça as correções necessárias para concluir seu cadastro</p>')))
            )
            layout.insert(
                1, Row(Column('message'), css_class='my-2'))
        elif self.instance.status == status.APPROVED:
            layout.insert(
                0,
                Row(Column(
                    HTML(f'<p class="h6 pt-2 text-success">{self.instance.message}</p>')))
            )

        return layout


class ApprovalWorkflowViewMixin:
    """
    Mixin to chango controls
    """

    def get_controls(self):
        """
        Default form controls list
        """
        controls = [ControlFactory.cancel_button(self.cancel_url)]

        if self.object is None:
            if self.model.initial_status_created:
                text = 'Enviar para análise'
            else:
                text = 'Salvar'
        elif self.object.status in [None, ApprovalWorkflow.Status.CREATED]:
            text = 'Salvar'
        elif self.object.status == ApprovalWorkflow.Status.WAITING:
            if self.request.user.is_superuser:
                text = 'Salvar'
            else:
                text = None
        else:
            text = 'Enviar para análise'

        if text:
            controls.append(ControlFactory.save_button(text=text))

        return controls
