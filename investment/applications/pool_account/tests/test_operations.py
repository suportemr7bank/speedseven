"""
Application test
"""
import os

from http import HTTPStatus
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clients.views.operations import ClientDepositView, ClientWithdrawView
from investment.models import ApplicationAccount, MoneyTransfer, ApplicationOp

#pylint: disable=no-member

User = get_user_model()


class TestClientDepositOperation(TestCase):
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
        self.user = User.objects.get(pk=2)

        self.client.login(email=self.user.email, password='qetu1234')
        self.app_acc = ApplicationAccount.objects.get(pk=1, user=self.user)
        self.deposit_url = reverse(
            'clients:deposit_create', kwargs={'pk': self.app_acc.pk})

        image_path = f'{os.getcwd()}/investment/tests/assets/aporte.png'
        with open(image_path, 'rb') as fp:
            self.receipt_file = SimpleUploadedFile(
                "aporte.png", fp.read(), content_type="image/png")

        MoneyTransfer.objects.all().delete()

    def test_first_deposit(self):
        """
        Test simple deposit
        """
        deposit_data = {
            'value': 10000,
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 1)

    def test_second_deposit(self):
        """
        Test simple deposit
        It must have balance to make deposit value less than 10000
        """
        ApplicationOp.make_deposit(
            application_account=self.app_acc,
            operator=self.user,
            value=10000
        )
        deposit_data = {'value': 1000, 'receipt_file': self.receipt_file}
        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 1)

    def test_first_deposit_value_fail(self):
        """
        Test simple deposit with invalid initial value
        """
        deposit_data = {
            'value': 1000,
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_first_deposit_value_zero_fail(self):
        """
        Test simple deposit with invalid initial value
        """
        deposit_data = {
            'value': 0,
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_first_deposit_negative_value_fail(self):
        """
        Test simple deposit with invalid initial value
        """
        deposit_data = {
            'value': -10000,
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_first_deposit_receipt_fail(self):
        """
        Test simple deposit without receipt
        """
        deposit_data = {
            'value': 10000,
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_deposit_not_approved_schedule(self):
        """
        Test simple deposit
        """
        deposit_data = {
            'value': 10000,
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        schedule = getattr(MoneyTransfer.objects.get(pk=1),
                           'accountopchedule', None)
        self.assertIsNone(schedule)

    @mock.patch('investment.interfaces.forms.OperationMixin._get_current_time') 
    def test_deposit_approved(self, mock_current_time):
        """
        Test deposit approved
        """
        deposit_data = {
            'value': 10000,
            'receipt_file': self.receipt_file
        }
        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.client.logout()

        self.user = User.objects.get(pk=1)
        self.client.login(email=self.user.email, password='qetu1234')

        approval_url = reverse(
            'investment:moneytransfer_approval', kwargs={'pk': MoneyTransfer.objects.get(pk=1).pk})

        approval_data = {
            'approve': 'approved'
        }

        curr_time = timezone.localtime(timezone.now())
        mock_current_time.return_value = curr_time

        response = self.client.post(
            path=approval_url, data=approval_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        term = self.app_acc.application.settings.deposit_term
        operation_date = timezone.localtime(
            curr_time + timezone.timedelta(days=term))

        schedule = getattr(MoneyTransfer.objects.get(pk=1),
                           'accountopschedule', None)

        self.assertEqual(schedule.operation_date, operation_date)

    def test_deposit_disapproved(self):
        """
        Test simple deposit
        """
        deposit_data = {
            'value': 10000,
            'receipt_file': self.receipt_file
        }
        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.client.logout()

        self.user = User.objects.get(pk=1)
        self.client.login(email=self.user.email, password='qetu1234')

        approval_url = reverse(
            'investment:moneytransfer_approval', kwargs={'pk': MoneyTransfer.objects.get(pk=1).pk})

        approval_data = {
            'approve': 'disapproved',
            'error_message': 'Comprovante inválido'
        }

        response = self.client.post(
            path=approval_url, data=approval_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        money_transfer = MoneyTransfer.objects.get(pk=1)

        self.assertEqual(money_transfer.state, MoneyTransfer.State.ERROR)

        schedule = getattr(MoneyTransfer.objects.get(pk=1),
                           'accountopschedule', None)

        self.assertIsNone(schedule)


class TestClientWithdrawOperation(TestCase):
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
        self.user = User.objects.get(pk=2)

        self.client.login(email=self.user.email, password='qetu1234')
        self.app_acc = ApplicationAccount.objects.get(pk=1, user=self.user)
        self.withdraw_url = reverse(
            'clients:withdraw_create', kwargs={'pk': self.app_acc.pk})

        image_path = f'{os.getcwd()}/investment/tests/assets/aporte.png'
        with open(image_path, 'rb') as fp:
            self.receipt_file = SimpleUploadedFile(
                "aporte.png", fp.read(), content_type="image/png")

        MoneyTransfer.objects.all().delete()
        ApplicationOp.objects.all().delete()

    def test_withdraw(self):
        """
        Test simple withdraw
        """

        ApplicationOp.make_deposit(
            application_account=self.app_acc, operator=self.user, value=2000)

        withdraw_data = {
            'value': 1000,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 1)

    def test_withdraw_fail_no_balance(self):
        """
        Test simple withdraw
        """
        withdraw_data = {
            'value': 1000,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsNotNone(
            response.context_data['form'].errors.get('__all__', None))

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_withdraw_fail_zero_value(self):
        """
        Test simple withdraw
        """
        withdraw_data = {
            'value': 0,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsNotNone(
            response.context_data['form'].errors.get('__all__', None))

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    def test_withdraw_fail_negative_value(self):
        """
        Test simple withdraw
        """
        withdraw_data = {
            'value': -10000,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsNotNone(
            response.context_data['form'].errors.get('__all__', None))

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()
        self.assertEqual(count, 0)

    @mock.patch('investment.interfaces.forms.OperationMixin._get_current_time')
    def test_withdraw_approved(self, mock_current_time):
        """
        Test simple withdraw
        """
        ApplicationOp.make_deposit(
            application_account=self.app_acc, operator=self.user, value=2000)

        withdraw_data = {
            'value': 1000,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)

        self.client.logout()

        self.user = User.objects.get(pk=1)
        self.client.login(email=self.user.email, password='qetu1234')

        approval_url = reverse(
            'investment:moneytransfer_approval', kwargs={'pk': MoneyTransfer.objects.get(pk=1).pk})

        approval_data = {
            'approve': 'approved'
        }

        curr_time = timezone.localtime(timezone.now())
        mock_current_time.return_value = curr_time

        response = self.client.post(
            path=approval_url, data=approval_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        term = self.app_acc.application.settings.withdraw_account_term
        operation_date = timezone.localtime(
            curr_time + timezone.timedelta(days=term))

        schedule = getattr(MoneyTransfer.objects.get(pk=1),
                           'accountopschedule', None)

        self.assertEqual(schedule.operation_date, operation_date)

    def test_withdraw_disapproved(self):
        """
        Test simple withdraw
        """
        ApplicationOp.make_deposit(
            application_account=self.app_acc, operator=self.user, value=2000)

        withdraw_data = {
            'value': 1000,
            'operation': ApplicationOp.OperationType.WITHDRAW_WALLET
        }

        with mock.patch.object(ClientWithdrawView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.withdraw_url, data=withdraw_data)

        self.client.logout()

        self.user = User.objects.get(pk=1)
        self.client.login(email=self.user.email, password='qetu1234')

        approval_url = reverse(
            'investment:moneytransfer_approval', kwargs={'pk': MoneyTransfer.objects.get(pk=1).pk})

        approval_data = {
            'approve': 'disapproved',
            'error_message': 'Comprovante inválido'

        }

        response = self.client.post(
            path=approval_url, data=approval_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        schedule = getattr(MoneyTransfer.objects.get(pk=1),
                           'accountopschedule', None)

        self.assertIsNone(schedule)
