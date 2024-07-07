# tests/test_token_generation.py

import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class TokenGenerationTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
        )

    def test_token_expiry(self):
        refresh = RefreshToken.for_user(self.user)
        token = str(refresh.access_token)
        
        # Check if token is expired
        self.assertFalse(refresh.access_token.is_expired())

        # Simulate token expiration
        future_time = timezone.now() + datetime.timedelta(seconds=3600)
        with self.settings(SIMPLE_JWT={'ACCESS_TOKEN_LIFETIME': datetime.timedelta(seconds=1)}):
            self.assertTrue(refresh.access_token.is_expired())

    def test_token_contains_user_details(self):
        refresh = RefreshToken.for_user(self.user)
        token = str(refresh.access_token)

        # Decode token payload
        decoded_token = RefreshToken(token)
        self.assertEqual(decoded_token['email'], self.user.email)
        self.assertEqual(decoded_token['first_name'], self.user.first_name)
        self.assertEqual(decoded_token['last_name'], self.user.last_name)
        # Add more assertions as needed

    def test_token_generation_for_anonymous_user(self):
        # Test token generation for an anonymous user
        refresh = RefreshToken.for_user(None)
        token = str(refresh.access_token)
        self.assertIsNotNone(token)
        # Add assertions for anonymous user token if needed

