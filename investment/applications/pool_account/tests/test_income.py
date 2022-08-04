"""
Application test
"""

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


from investment.models import ApplicationAccount, ApplicationOp
from ..models import IncomeOperation, AccountSettings

#pylint: disable=no-member

User = get_user_model()
settings.INCOME_OPERATION_RUN_IN_BACKGROUND = False


class TestIncomeOperation(TestCase):
    """
    Test application dependent deposit operation
    """

    fixtures = [
        'core/fixtures/users.json',
        'clients/fixtures/clients.json',
        'accounts/fixtures/roles.json',
        'products/fixtures/products.json',
        'pool_account.json',
        'applications'
    ]

    def setUp(self):
        self.operator = User.objects.get(pk=1)
        self.user = User.objects.get(pk=2)

        self.client.login(email=self.operator.email, password='qetu1234')
        self.app_acc1 = ApplicationAccount.objects.get(pk=1, user=self.user)
        self.app_acc2 = ApplicationAccount.objects.get(pk=2, user=self.user)
        self.income_url = reverse(
            'investment:application_operation', kwargs={'pk': self.app_acc1.pk})

    def make_deposit(self, value, operation_date, application_account):
        """ Make deposit """
        ApplicationOp.make_deposit(
            operator=self.operator,
            application_account=application_account,
            operation_date=operation_date,
            value=value
        )

    def make_withdraw(self, value, operation_date, app_acc):
        """ Make withdraw """
        ApplicationOp.make_withdraw(
            operator=self.operator,
            application_account=app_acc,
            operation_date=operation_date,
            operation_type=ApplicationOp.OperationType.WITHDRAW_WALLET,
            value=value
        )

    def operation_date(self, day, month=6, hour=0):
        """ Operation date """
        return timezone.localtime(
            timezone.make_aware(
                timezone.datetime(year=2022, month=month, day=day, hour=hour)
            )
        )

    def income_date(self, month=6):
        """Income date. Day has no relevance"""
        return timezone.datetime(year=2022, month=month, day=1).strftime('%d/%m/%Y')

    def post_income(self, full_rate, costs_rate, net_rate, paid_rate=1.0, income_date=None):
        """ Post income and return response"""
        if not income_date:
            income_date = self.income_date()
        data = {
            'income_date': income_date,
            'full_rate': full_rate, 'costs_rate': costs_rate,
            'net_rate': net_rate, 'paid_rate': paid_rate
        }
        return self.client.post(self.income_url, data=data)

    def test_income_creation(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        response = self.post_income(4.3, 1.7, 2.6)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        count = IncomeOperation.objects.filter(pk=1).count()
        self.assertEqual(1, count)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.operation_type,
                         ApplicationOp.OperationType.INCOME)

    def test_income_deposit_datetime(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        self.post_income(4.3, 1.7, 2.6)

        income_deposti_date = self.operation_date(
            day=30).replace(hour=23, minute=59, second=59)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.operation_date, income_deposti_date)

    def test_income_creation_twice_in_month_fail(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        response = self.post_income(4.3, 1.7, 2.6)

        response = self.post_income(4.3, 1.7, 2.6)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # An income operation already exists in thie month
        self.assertIsNotNone(
            response.context_data['form'].errors.get('income_date', None))

    def test_income_no_balance(self):
        """ Test income canculation without any previous deposit"""
        response = self.post_income(4.3, 1.7, 2.6)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        acc_op = ApplicationOp.objects.last()
        self.assertIsNone(acc_op)

    def test_income_creation_dep_first_day(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        response = self.post_income(4.3, 1.7, 2.6, paid_rate=1.5)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, 150)
        self.assertEqual(acc_op.balance, 10150)

    def test_income_creation_dep_last_day(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=30)
        self.make_deposit(10000, operation_date, self.app_acc1)

        response = self.post_income(4.3, 1.7, 2.6, 1.5)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, 5)
        self.assertEqual(acc_op.balance, 10005)

    def test_income_last_month_income(self):
        """ Test income canculation with last month income operation"""
        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=10,
            balance=1010,
        )

        self.post_income(4.3, 1.7, 2.6, paid_rate=1.0)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, 10.1)
        self.assertEqual(acc_op.balance, 1020.1)

    def test_income_creation_twice(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        self.post_income(4.3, 1.7, 2.6)

        income_date = self.income_date(month=7)
        response = self.post_income(4.3, 1.7, 2.6, income_date=income_date)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        income_deposit_date = self.operation_date(
            day=31, month=7).replace(hour=23, minute=59, second=59)

        self.assertEqual(3, ApplicationOp.objects.all().count())

        count = ApplicationOp.objects.filter(
            operation_type=ApplicationOp.OperationType.INCOME).count()
        self.assertEqual(2, count)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.operation_type,
                         ApplicationOp.OperationType.INCOME)
        self.assertEqual(acc_op.operation_date, income_deposit_date)
        self.assertEqual(acc_op.value, 101)
        self.assertEqual(acc_op.balance, 10201)

    def test_income_creation_twice_skip_month(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        self.post_income(4.3, 1.7, 2.6)

        income_date = self.income_date(month=8)
        response = self.post_income(4.3, 1.7, 2.6, income_date=income_date)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsNotNone(
            response.context_data['form'].errors.get('income_date', None))

    def test_income_creation_twice_prev_month(self):
        """ Test income canculation """
        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)

        self.post_income(4.3, 1.7, 2.6)

        income_date = self.income_date(month=5)
        response = self.post_income(4.3, 1.7, 2.6, income_date=income_date)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsNotNone(
            response.context_data['form'].errors.get('income_date', None))

    def test_income_many_deposits(self):
        """ Test income canculation """

        value = [10000, 2000, 1500, 100]
        balance = [10000, 12000, 13500, 13600]

        operation_date = self.operation_date(day=1)
        self.make_deposit(value[0], operation_date, self.app_acc1)

        operation_date = self.operation_date(day=10)
        self.make_deposit(value[1], operation_date, self.app_acc1)

        operation_date = self.operation_date(day=20)
        self.make_deposit(value[2], operation_date, self.app_acc1)

        operation_date = self.operation_date(day=29)
        self.make_deposit(value[3], operation_date, self.app_acc1)

        paid_rate = 1.5

        income = (
            9 * balance[0] +
            10 * balance[1] +
            9 * balance[2] +
            2 * balance[3]) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, income)

    def test_opened_month_no_operation(self):
        """ Test income canculation """

        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=10000,
        )

        paid_rate = 1.5

        income = (30 * 10000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_opened_month_first_day_deposit(self):
        """ Test income canculation """

        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=10000,
        )

        operation_date = self.operation_date(day=1)
        self.make_deposit(1000, operation_date, self.app_acc1)

        paid_rate = 1.5

        # day 1 - 17
        income = (30 * 11000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_opened_month_middle_deposit(self):
        """ Test income canculation """

        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=10000,
        )

        operation_date = self.operation_date(day=17)
        self.make_deposit(1000, operation_date, self.app_acc1)

        paid_rate = 1.5

        # day 1 - 17
        income = (16 * 10000 + 14 * 11000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_opened_first_day_middle_deposit(self):
        """ Test income canculation """

        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=10000,
        )

        operation_date = self.operation_date(day=1)
        self.make_deposit(1000, operation_date, self.app_acc1)

        operation_date = self.operation_date(day=17)
        self.make_deposit(1000, operation_date, self.app_acc1)

        paid_rate = 1.5

        # day 1 - 17
        income = (16 * 11000 + 14 * 12000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_open_middle_deposit(self):
        """ Test income canculation """

        operation_date = self.operation_date(day=17)
        self.make_deposit(10000, operation_date, self.app_acc1)

        paid_rate = 1.5

        # includding month last day (30 - 17 + 1)
        days = 14

        income = (days * 10000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_income_init_month_deposit_withdraw_middle(self):
        """ Test income canculation """

        # [depisit, withdraw]
        value = [10000, 7000]
        balance = [10000, 3000]

        operation_date = self.operation_date(day=1)
        self.make_deposit(value[0], operation_date, self.app_acc1)

        operation_date = self.operation_date(day=13)
        self.make_withdraw(value[1], operation_date, self.app_acc1)

        paid_rate = 1.5

        income = (
            12 * balance[0] +
            18 * balance[1]) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_income_init_month_deposit_full_withdraw_middle(self):
        """ Test income canculation """

        # [depisit, withdraw]
        value = [10000, 10000]
        balance = [10000, 0]

        operation_date = self.operation_date(day=1)
        self.make_deposit(value[0], operation_date, self.app_acc1)

        operation_date = self.operation_date(day=13)
        self.make_withdraw(value[1], operation_date, self.app_acc1)

        paid_rate = 1.5

        income = (
            12 * balance[0] +
            18 * balance[1]) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_opened_full_withdraw_first_day(self):
        """ Test income canculation """
        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=2000,
        )

        operation_date = self.operation_date(day=1)
        self.make_withdraw(2000, operation_date, self.app_acc1)

        acc_op_w = ApplicationOp.objects.last()
        self.assertEqual(acc_op_w.balance, 0)

        self.post_income(4.3, 1.7, 2.6, paid_rate=1.5)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op, acc_op_w)

    def test_opened_full_withdraw_last_day(self):
        """ Test income canculation """
        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=2000,
        )

        operation_date = self.operation_date(day=30)
        self.make_withdraw(2000, operation_date, self.app_acc1)

        paid_rate = 1.5

        income = (29 * 2000) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.value, round(income, 2))

    def test_opened_partial_withdraw_first_day(self):
        """ Test income canculation """
        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=2000,
        )

        operation_date = self.operation_date(day=11)
        self.make_withdraw(2000, operation_date, self.app_acc1)

        self.post_income(4.3, 1.7, 2.6, paid_rate=1.5)

        acc_op = ApplicationOp.objects.last()
        self.assertEqual(acc_op.operation_type,
                         ApplicationOp.OperationType.INCOME)

    def test_two_applications(self):
        """ Test two applications """

        operation_date = self.operation_date(31, month=5)
        ApplicationOp.make_income_deposit(
            application_account_id=self.app_acc1.pk,
            operation_date=operation_date,
            operator_id=self.user.pk,
            value=1000,
            balance=2000,
        )
        operation_date = self.operation_date(day=13)
        self.make_deposit(13749.37, operation_date, self.app_acc1)

        operation_date = self.operation_date(day=1)
        self.make_deposit(12000, operation_date, self.app_acc2)
        operation_date = self.operation_date(day=17)
        self.make_deposit(1200, operation_date, self.app_acc2)

        paid_rate = 1.5

        income1 = (12 * 2000 + 18 * 15749.37) / 30 * paid_rate / 100

        income2 = (16 * 12000 + 14 * 13200) / 30 * paid_rate / 100

        self.post_income(4.3, 1.7, 2.6, paid_rate=paid_rate)

        acc_op = ApplicationOp.objects.filter(
            application_account=self.app_acc1).last()
        self.assertEqual(acc_op.value, round(income1, 2))

        acc_op = ApplicationOp.objects.filter(
            application_account=self.app_acc2).last()
        self.assertEqual(acc_op.value, round(income2, 2))

    def test_custom_paid_rate(self):
        """ Test income canculation """
        acc_set = AccountSettings.objects.get(
            application_account=self.app_acc1)
        acc_set.custom_rate = 2
        acc_set.save()

        AccountSettings.objects.create(
            application_account=self.app_acc2, custom_rate=1.8)

        operation_date = self.operation_date(day=1)
        self.make_deposit(10000, operation_date, self.app_acc1)
        self.make_deposit(20000, operation_date, self.app_acc2)

        response = self.post_income(4.3, 1.7, 2.6, paid_rate=1.5)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        acc_op = ApplicationOp.objects.filter(
            application_account=self.app_acc1).last()
        self.assertEqual(acc_op.value, 200)
        self.assertEqual(acc_op.balance, 10200)

        acc_op = ApplicationOp.objects.filter(
            application_account=self.app_acc2).last()
        self.assertEqual(acc_op.value, 360)
        self.assertEqual(acc_op.balance, 20360)
