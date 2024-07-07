from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

class RegistrationEndpointTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'  # Ensure this path matches your URL configuration

    def test_successful_registration(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword",
            "phone": "1234567890"
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], data['firstName'])
        self.assertEqual(response.data['data']['user']['lastName'], data['lastName'])

    def test_missing_required_fields(self):
        data = {
            "firstName": "John",
            "lastName": "",  # Missing lastName
            "email": "john.doe@example.com",
            "password": "securepassword",
            "phone": "1234567890"
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

    def test_duplicate_email(self):
        User = get_user_model()
        User.objects.create_user(
            email='existing@example.com',
            password='testpassword',
            first_name='Existing',
            last_name='User'
        )

        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "existing@example.com",  # Duplicate email
            "password": "securepassword",
            "phone": "1234567890"
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
