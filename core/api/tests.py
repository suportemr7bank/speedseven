""" Core api test """
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts import roles


class TestAuhetication(TestCase):
    """
    Authentication test
    """

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.api_user = user_model.objects.create(
            username='api@speedseven.com', email='api@speedseven.com')
        cls.api_user.set_password('qetu1234')
        cls.api_user.save()
        roles.create_user_role(cls.api_user, roles.Roles.APIACC)

        cls.app_user = user_model.objects.create(username='speedseven_api')
        cls.app_user.set_password('qetu1234')
        cls.app_user.save()
        roles.create_user_role(cls.app_user, roles.Roles.APIAPP)

    def test_unauthorized_token_request(self):
        """Test token request"""
        factory = APIClient()
        data = {
            'username': 'unauthorized@speedseven.com',
            'password': 'qetu1234'
        }
        request = factory.post('/api/token/', data, format='json')
        self.assertEqual(request.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_token_request_wrong_pass(self):
        """Test token request"""
        factory = APIClient()
        data = {
            'username': 'api@speedseven.com',
            'password': 'qetu123'
        }
        request = factory.post('/api/token/', data, format='json')
        self.assertEqual(request.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_user_token_request(self):
        """Test token request"""
        factory = APIClient()
        data = {
            'username': 'api@speedseven.com',
            'password': 'qetu1234'
        }
        request = factory.post('/api/token/', data, format='json')
        self.assertEqual(request.status_code, HTTPStatus.OK)

    def test_authorized_app_token_request(self):
        """Test token request"""
        factory = APIClient()
        data = {
            'username': 'speedseven_api',
            'password': 'qetu1234'
        }
        request = factory.post('/api/token/', data, format='json')
        self.assertEqual(request.status_code, HTTPStatus.OK)
