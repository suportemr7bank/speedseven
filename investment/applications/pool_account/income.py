"""
Income class
"""

import calendar
from itertools import islice

from django.db import models
from django.db.models import Case, F, Max, Value, When
from django.db.models.functions import ExtractDay
from django.utils import timezone
from investment.models import ApplicationAccount, ApplicationOp

from .models import IncomeOperation


class IncomeCalculation:
    """
    Income calculation
    """

    operation_saving_batch_size = 500

    @classmethod
    def run_income_operation(cls, income_op, progress_notifyer):
        """
        Run instance operation
        """
        if income_op.state == IncomeOperation.State.WATING:
            

            income_op.state = IncomeOperation.State.RUNNING
            curr_date = timezone.localtime(timezone.now())
            income_op.date_started = curr_date
            income_op.save()

            # pylint: disable=no-member
            progress_notifyer('Calculando rendimento...')
            # Current month operation
            month_ops = cls._current_month_operations(
                income_op.application, income_op.income_date)

            # Operation in current month but without first day operation
            first_day_ops = cls._first_day_operations(
                income_op.application, income_op.income_date)

            # Application account custom taxes
            custom_taxes = cls._custom_taxes(
                income_op.application, income_op.paid_rate)

            app_ops = cls._to_dict(first_day_ops, month_ops)

            month_ops_objs = cls._calculate_income(
                app_ops, custom_taxes, income_op.income_date, income_op.operator)

            all_objects = month_ops_objs

            cls._make_operations(all_objects, progress_notifyer)

            income_op.state = IncomeOperation.State.FINISHED
            curr_date = timezone.localtime(timezone.now())
            income_op.date_finished = curr_date
            income_op.save()

    @classmethod
    def _to_dict(cls, first_day_ops, month_ops):
        ops = dict()

        pks = set(list(first_day_ops.values_list('application_account_id', flat=True))).union(
            set(list(month_ops.values_list('application_account_id', flat=True))))

        pks = list(pks)

        for _pk in pks:
            ops[_pk] = []

        for data in first_day_ops:
            ops[data['application_account_id']].append(
                {'day': data['day'], 'balance': data['balance']})

        for data in month_ops:
            ops[data['application_account_id']].append(
                {'day': data['day'], 'balance': data['balance']})

        return ops

    @classmethod
    def _make_operations(cls, operation_objects, progress_notifyer):
        # Save applicationops in batches for optimization
        batch_size = cls.operation_saving_batch_size
        iterrator = iter([x for x in operation_objects])
        total = len(operation_objects)
        recorded = 0
        while True:
            batch = list(islice(iterrator, batch_size))
            if not batch:
                progress_notifyer('Realizando operações: 100%')
                break
            # pylint: disable=no-member
            ApplicationOp.objects.bulk_create(batch, batch_size)
            recorded += len(batch)
            progress = recorded / total
            progress_notifyer(f'Realizando operações: {(progress*100):.2f}%')

        progress_notifyer('Realizando operações: 100%')

    @classmethod
    def _calculate_income(cls, app_ops, custom_taxes, income_date, operator):
        # pylint: disable=no-member

        month_days = calendar.monthrange(
            income_date.year, income_date.month)[1]
        operation_date = cls._operation_date(income_date, month_days)

        operation_income = ApplicationOp.OperationType.INCOME

        income_operations = []

        for app_acc_id, operations in app_ops.items():
            rate = custom_taxes[app_acc_id]
            income = 0
            balance = 0
            count = len(operations)

            # Last day deposit is computed in the next month
            if count > 1:
                for i in range(1, count):
                    days = operations[i]['day'] - operations[i-1]['day']
                    prop_rate = rate * (days / month_days) / 100
                    value = operations[i-1]['balance'] * prop_rate
                    income += value

                # Last operation until the month end
                days = month_days - operations[i]['day'] + 1
                if days >= 1:
                    prop_rate = rate * (days / month_days) / 100
                    value = operations[i]['balance'] * prop_rate
                    income += value
                balance = operations[i]['balance']

            elif count == 1:
                if operations[0]['balance'] > 0:
                    days = month_days - operations[0]['day'] + 1
                    prop_rate = rate * (days / month_days) / 100
                    value = operations[0]['balance'] * prop_rate
                    income += value
                    balance = operations[0]['balance']

            round_income = round(income, 2)
            round_balance = round(income+balance, 2)

            if round_income > 0:
                income_operations.append(
                    ApplicationOp(
                        application_account_id=app_acc_id,
                        operation_date=operation_date,
                        value=round_income,
                        balance=round_balance,
                        operation_type=operation_income,
                        description='Rendimento',
                        operator=operator
                    )
                )

        return income_operations

    @classmethod
    def _operation_date(cls, income_date, month_days):
        _dt = timezone.datetime
        # pylint: disable=no-member
        date = income_date.replace(day=month_days)
        date = timezone.localtime(timezone.make_aware(
            _dt.combine(date, _dt.min.time())))
        operation_date = date.replace(
            hour=23, minute=59, second=59, microsecond=0)
        return operation_date

    @classmethod
    def _current_month_operations(cls, application, operation_date):
        # pylint: disable=no-member
        last_op_day_pks = ApplicationOp.objects.filter(
            application_account__is_active=True,
            application_account__application=application,
            operation_date__year=operation_date.year,
            operation_date__month=operation_date.month
        ).annotate(
            day=ExtractDay('operation_date'),
        ).values(
            'day'
        ).annotate(
            last_op=Max('pk')
        ).order_by(
            'last_op', 'application_account', 'day'
        ).values_list('last_op', flat=True)

        app_month_ops = ApplicationOp.objects.filter(
            pk__in=list(last_op_day_pks)
        ).annotate(
            day=ExtractDay('operation_date')
        ).values(
            'application_account_id', 'balance', 'day'
        ).order_by(
            'application_account_id', 'day'
        )

        return app_month_ops

    @classmethod
    def _first_day_operations(cls, application, operation_date):

        prev_month = (timezone.datetime(
            year=operation_date.year,
            month=operation_date.month,
            day=1).date() - timezone.timedelta(days=1)).month

        not_first_day_op = cls._not_first_day_op(application, operation_date)
        in_last_month = cls._in_last_month(
            application, operation_date, prev_month)
        app_acc = not_first_day_op + in_last_month

        # pylint: disable=no-member
        app_ops_pks = ApplicationOp.objects.filter(
            application_account__pk__in=app_acc,
            operation_date__year=operation_date.year,
            operation_date__month=prev_month,
            operation_type=ApplicationOp.OperationType.INCOME
        ).annotate(
            day=ExtractDay('operation_date')
        ).annotate(
            max_pk=Max('pk')
        ).values(
            'pk'
        )

        # pylint: disable=no-member
        app_ops = ApplicationOp.objects.filter(
            pk__in=app_ops_pks
        ).annotate(
            day=Value(1, output_field=models.IntegerField())
        ).values(
            'application_account_id', 'balance', 'day'
        ).order_by(
            'application_account_id', 'day'
        )

        return app_ops

    @classmethod
    def _not_first_day_op(cls, application, operation_date):
        # pylint: disable=no-member
        app_acc = ApplicationAccount.objects.filter(
            application=application,
            is_active=True,
            applicationop__operation_date__year=operation_date.year,
            applicationop__operation_date__month=operation_date.month,
        ).exclude(
            applicationop__operation_date__day=1
        ).values_list('pk', flat=True)
        return list(app_acc.values_list('pk', flat=True))

    @classmethod
    def _in_last_month(cls, application, operation_date, prev_month):
        # pylint: disable=no-member
        app_acc = ApplicationAccount.objects.exclude(
            applicationop__operation_date__year=operation_date.year,
            applicationop__operation_date__month=operation_date.month,
        ).filter(
            is_active=True,
            application=application,
            applicationop__operation_date__year=operation_date.year,
            applicationop__operation_date__month=prev_month
        ).values_list('pk', flat=True)
        return list(app_acc.values_list('pk', flat=True))

    @classmethod
    def _custom_taxes(cls, application, paid_rate):
        # pylint: disable=no-member
        custom_taxes = application.applicationaccount_set.filter(
            is_active=True
        ).annotate(
            rate=Case(
                When(
                    accountsettings__custom_rate__isnull=True,
                    then=Value(paid_rate,
                               output_field=models.FloatField())
                ),
                default=F('accountsettings__custom_rate')
            ),
            application_account_id=F('pk')
        ).values_list(
            'application_account_id', 'rate'
        )
        return dict(custom_taxes)
