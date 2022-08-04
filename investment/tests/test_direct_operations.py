"""
Test operations
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from investment.models import ApplicationAccount, ApplicationOp
from investment.operations import exceptions as ex
from investment.operations.operations import ApplicationAccountOperation

# pylint: disable=missing-function-docstring
# pylint: disable=no-member

User = get_user_model()


class TestDepositValidation(TestCase):
    """
    Test direct deposit operation
    Direct deposit is available only to admin
    """

    fixtures = [
        'core/fixtures/users.json',
        'clients/fixtures/clients.json',
        'applications'
    ]

    def setUp(self) -> None:
        self.operator = User.objects.get(pk=1)
        self.app_acc_op = ApplicationAccountOperation()
        self.app_acc = ApplicationAccount.objects.get(pk=1)
        return super().setUp()

    def test_ok(self):
        value = 100.00
        self.app_acc_op.validate_deposit(self.app_acc, value)

    def test_operation_date_ok(self):
        value = 100.00
        operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.validate_deposit(self.app_acc, value, operation_date)

    def test_invalid_app_acc(self):
        value = 100.0
        app_acc = None
        with self.assertRaises(ex.InvalidApplicationError):
            self.app_acc_op.validate_deposit(app_acc, value)

    def test_inactive_app_acc(self):
        value = 100.0
        self.app_acc.is_active = False
        self.app_acc.save()
        with self.assertRaises(ex.InactiveApplicationError):
            self.app_acc_op.validate_deposit(self.app_acc, value)

    def test_invalid_value_zero(self):
        value = 0
        with self.assertRaises(ex.DepositValueError):
            self.app_acc_op.validate_deposit(self.app_acc, value)

    def test_invalid_value_negative(self):
        value = -100.0
        with self.assertRaises(ex.DepositValueError):
            self.app_acc_op.validate_deposit(self.app_acc, value)

    def test_same_operation_date(self):
        value = 100.0
        operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value, 'Initial deposit', operation_date)
        with self.assertRaises(ex.SameOperationDateError):
            self.app_acc_op.validate_deposit(
                self.app_acc, value, operation_date)

    def test_retroactive_operation_date(self):
        value = 100.0
        operation_date = timezone.localtime(timezone.now())
        retroactive_date = operation_date - timezone.timedelta(days=1)
        self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value, 'Initial deposit', operation_date)
        with self.assertRaises(ex.ReatroactiveOperationDateError):
            self.app_acc_op.validate_deposit(
                self.app_acc, value, retroactive_date)


class TestWithdrawValidation(TestCase):
    """
    Test direct withdraw operation
    Direct withdraw is available only to admin
    """

    fixtures = [
        'core/fixtures/users.json',
        'clients/fixtures/clients.json',
        'applications'
    ]

    def setUp(self) -> None:
        self.operator = User.objects.get(pk=1)
        self.app_acc_op = ApplicationAccountOperation()
        self.app_acc = ApplicationAccount.objects.get(pk=1)

        value = 1000
        self.operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value, 'Initial deposit', self.operation_date)

        self.op_type = ApplicationOp.OperationType.WITHDRAW_WALLET

        return super().setUp()

    def test_ok(self):
        value = 100.00
        self.app_acc_op.validate_withdraw(self.app_acc, value, self.op_type)

    def test_operation_date_ok(self):
        value = 100.00
        operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.validate_withdraw(
            self.app_acc, value, self.op_type, operation_date)

    def test_invalid_app_acc(self):
        value = 100.0
        app_acc = None
        with self.assertRaises(ex.InvalidApplicationError):
            self.app_acc_op.validate_withdraw(app_acc, value, self.op_type)

    def test_inactive_app_acc(self):
        value = 100.0
        self.app_acc.is_active = False
        self.app_acc.save()
        with self.assertRaises(ex.InactiveApplicationError):
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type)

    def test_invalid_value_zero(self):
        value = 0
        with self.assertRaises(ex.WithdrawValueError):
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type)

    def test_invalid_value_negative(self):
        value = -100.0
        with self.assertRaises(ex.WithdrawValueError):
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type)

    def test_invalid_no_balance(self):
        value = 1000.1
        with self.assertRaises(ex.WithdrawNotEnoughBalanceError):
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type)

    def test_withdraws_max_balance(self):
        value = 1000
        self.app_acc_op.validate_withdraw(self.app_acc, value, self.op_type)

    def test_same_operation_date(self):
        value = 100.0
        with self.assertRaises(ex.SameOperationDateError):
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type, self.operation_date)

    def test_retroactive_operation_date(self):
        value = 100.0
        with self.assertRaises(ex.ReatroactiveOperationDateError):
            retroactive_date = self.operation_date - timezone.timedelta(days=1)
            self.app_acc_op.validate_withdraw(
                self.app_acc, value, self.op_type, retroactive_date)


class TestDepositOperation(TestCase):
    """
    Test direct deposit operation
    Direct deposit is available only to admin
    """

    fixtures = [
        'core/fixtures/users.json',
        'clients/fixtures/clients.json',
        'applications'
    ]

    def setUp(self) -> None:
        self.operator = User.objects.get(pk=1)
        self.app_acc_op = ApplicationAccountOperation()
        self.app_acc = ApplicationAccount.objects.get(pk=1)
        return super().setUp()

    def test_initial_deposit_state(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        app_op = ApplicationOp.objects.get(pk=1)
        self.assertEqual(app_op.operation_type,
                         ApplicationOp.OperationType.OPEN)

    def test_initial_deposit(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        count = ApplicationOp.objects.count()
        self.assertEqual(count, 1)

    def test_operation_date(self):
        value = 1000
        operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value, operation_date=operation_date)
        obj = ApplicationOp.objects.get(pk=1)
        self.assertEqual(obj.operation_date, operation_date)

    @patch('investment.models.get_operation_date')
    def test_auto_operation_date(self, mock_op_date):
        value = 1000
        operation_date = timezone.localtime(timezone.now())
        mock_op_date.return_value = operation_date
        self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value)
        obj = ApplicationOp.objects.get(pk=1)
        self.assertEqual(obj.operation_date, operation_date)

    def test_initial_deposit_value(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        app_op = ApplicationOp.objects.get(pk=1)
        self.assertEqual(app_op.value, value)

    def test_initial_deposit_balance(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        app_op = ApplicationOp.objects.get(pk=1)
        self.assertEqual(app_op.balance, value)

    def test_next_deposit_state(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.operation_type,
                         ApplicationOp.OperationType.DEPOSIT)

    def test_next_deposit_value(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        next_value = 1001
        self.app_acc_op.make_deposit(self.operator, self.app_acc, next_value)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.value, next_value)

    def test_next_deposit_balance(self):
        value = 1000
        self.app_acc_op.make_deposit(self.operator, self.app_acc, value)
        next_value = 1001
        self.app_acc_op.make_deposit(self.operator, self.app_acc, next_value)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.balance, value + next_value)


class TestWithdrawOperation(TestCase):
    """
    Test direct deposit operation
    Direct deposit is available only to admin
    """

    fixtures = [
        'core/fixtures/users.json',
        'clients/fixtures/clients.json',
        'applications'
    ]

    def setUp(self) -> None:
        self.operator = User.objects.get(pk=1)
        self.app_acc_op = ApplicationAccountOperation()
        self.app_acc = ApplicationAccount.objects.get(pk=1)
        value = 1000
        # Start with a deposit to ensure balance available
        # Next operations have pk > 1
        self.balance = self.app_acc_op.make_deposit(
            self.operator, self.app_acc, value).balance

        return super().setUp()

    def test_withdraw_wallet(self):
        value = 100
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_WALLET)
        count = ApplicationOp.objects.count()
        self.assertEqual(count, 2)

    def test_withdraw_income(self):
        value = 100
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_INCOME)
        count = ApplicationOp.objects.count()
        self.assertEqual(count, 2)

    def test_value(self):
        value = 100
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_WALLET)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.value, value)

    def test_balance(self):
        value = 300
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_WALLET)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.balance, self.balance - value)

    def test_max_balance(self):
        value = self.balance
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_WALLET)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.balance, 0)

    def test_two_balance(self):
        value1 = 300
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value1, ApplicationOp.OperationType.WITHDRAW_WALLET)
        value2 = 437
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value2, ApplicationOp.OperationType.WITHDRAW_WALLET)
        app_op = ApplicationOp.objects.get(pk=3)
        self.assertEqual(app_op.balance, self.balance - (value1 + value2))

    def test_close_invalid_app_opp(self):
        """
        Close operation makes a witdraw to zero balance
        and then makes another operation to close account
        The close generates two account op entries
        """
        with self.assertRaises(ex.InvalidApplicationError):
            self.app_acc_op.close_application(self.operator, None)

    def test_close_inactive_app_opp(self):
        """
        Close operation makes a witdraw to zero balance
        and then makes another operation to close account
        The close generates two account op entries
        """
        with self.assertRaises(ex.InactiveApplicationError):
            self.app_acc.is_active = False
            self.app_acc.save()
            self.app_acc_op.close_application(self.operator, self.app_acc)

    def test_close_app_opp_withdraw_state(self):
        """
        Close operation makes a witdraw to zero balance
        and then makes another operation to close account
        The close generates two account op entries
        """
        self.app_acc_op.close_application(self.operator, self.app_acc)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.operation_type,
                         ApplicationOp.OperationType.WITHDRAW_WALLET)

    def test_close_app_opp_value(self):
        """
        The withdraw operation before closing. Indicates a withdraw to zero balance.
        """
        self.app_acc_op.close_application(self.operator, self.app_acc)
        app_op = ApplicationOp.objects.get(pk=2)
        self.assertEqual(app_op.value, self.balance)
        self.assertEqual(app_op.balance, 0)

    def test_close_app_opp_balance(self):
        """
        The close application operation value and balance are 0
        """
        self.app_acc_op.close_application(self.operator, self.app_acc)
        app_op = ApplicationOp.objects.get(pk=3)
        self.assertEqual(app_op.value, 0)
        self.assertEqual(app_op.balance, 0)

    def test_close_app_opp_state(self):
        """
        The close application operation. Only sets operation type to CLOSE
        """
        self.app_acc_op.close_application(self.operator, self.app_acc)
        app_op = ApplicationOp.objects.get(pk=3)
        self.assertEqual(app_op.operation_type,
                         ApplicationOp.OperationType.CLOSE)

    def test_operation_date(self):
        value = 100
        operation_date = timezone.localtime(timezone.now())
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value,
            ApplicationOp.OperationType.WITHDRAW_WALLET, operation_date=operation_date)
        obj = ApplicationOp.objects.get(pk=2)
        self.assertEqual(obj.operation_date, operation_date)

    @patch('investment.models.get_operation_date')
    def test_auto_operation_date(self, mock_op_date):
        value = 100
        operation_date = timezone.localtime(timezone.now())
        mock_op_date.return_value = operation_date
        self.app_acc_op.make_withdraw(
            self.operator, self.app_acc, value, ApplicationOp.OperationType.WITHDRAW_WALLET)
        obj = ApplicationOp.objects.get(pk=2)
        self.assertEqual(obj.operation_date, operation_date)
