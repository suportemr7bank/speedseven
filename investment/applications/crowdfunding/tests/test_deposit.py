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

from clients.views.operations import ClientDepositView
from investment.models import ApplicationAccount, MoneyTransfer

from ..models import ApplicationSettings

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
        'crowdfunding.json',
        'applications'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=2)

        self.client.login(email=self.user.email, password='qetu1234')
        self.app_acc = ApplicationAccount.objects.get(pk=3, user=self.user)
        self.app_settings = self.app_acc.application.settings
        self.deposit_url = reverse(
            'clients:deposit_create', kwargs={'pk': self.app_acc.pk})

        image_path = f'{os.getcwd()}/investment/tests/assets/aporte.png'
        with open(image_path, 'rb') as fp:
            self.receipt_file = SimpleUploadedFile(
                "aporte.png", fp.read(), content_type="image/png")

        MoneyTransfer.objects.all().delete()

    def test_deposit_not_opened(self):
        """
        Test deposit operation not opened (opened to purchase product)
        """
        deposit_data = {
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()

        self.assertEqual(count, 0)

    def test_deposit_opened(self):
        """
        Test deposit operation opened to deposit
        """
        self.app_settings.state = ApplicationSettings.State.OPEN_DEPOSIT
        self.app_settings.save()

        deposit_data = {
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()

        self.assertEqual(count, 1)


    def test_deposit_value(self):
        """
        Test deposit operation opened to deposit
        """
        self.app_settings.state = ApplicationSettings.State.OPEN_DEPOSIT
        self.app_settings.save()

        deposit_data = {
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

        money_transfer = MoneyTransfer.objects.last()

        # Client can not change deposit value
        self.assertEqual(money_transfer.value, self.app_settings.min_deposit)
        self.assertEqual(money_transfer.state, MoneyTransfer.State.CREATED)


    def test_deposit_fail(self):
        """
        Test deposit operation fail (without receipt)
        """
        self.app_settings.state = ApplicationSettings.State.OPEN_DEPOSIT
        self.app_settings.save()

        deposit_data = {
            'receipt_file':""
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()

        self.assertEqual(count, 0)

    def test_deposit_cancelled(self):
        """
        Test deposit operation cancelled to deposit
        """
        self.app_settings.state = ApplicationSettings.State.CANCELLED
        self.app_settings.save()

        deposit_data = {
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()

        self.assertEqual(count, 0)

    def test_deposit_completed(self):
        """
        Test deposit operation completed to deposit
        """
        self.app_settings.state = ApplicationSettings.State.COMPLETED
        self.app_settings.save()

        deposit_data = {
            'receipt_file': self.receipt_file
        }

        with mock.patch.object(ClientDepositView, 'skip_signup_test', True):
            response = self.client.post(
                path=self.deposit_url, data=deposit_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        count = MoneyTransfer.objects.filter(
            application_account=self.app_acc).count()

        self.assertEqual(count, 0)

