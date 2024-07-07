from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from userapp.utils import create_access_token
from userapp.models import Organisation

class OrganisationAccessTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            username='user1@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2@example.com',
            password='password456',
            first_name='Jane',
            last_name='Smith',
        )
        self.org1 = Organisation.objects.create(
            name="John's Organisation",
            description="John's Organization Description",
        )
        self.org2 = Organisation.objects.create(
            name="Jane's Organisation",
            description="Jane's Organization Description",
        )
        self.org1.users.add(self.user1)  # User1 belongs to Org1
        self.org2.users.add(self.user2)  # User2 belongs to Org2

    def test_get_own_organisations(self):
        # User1 should only see Org1
        url = reverse('organisation-list')
        access_token = create_access_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['organisations']), 1)
        self.assertEqual(response.data['data']['organisations'][0]['name'], "John's Organisation")

    def test_get_single_organisation(self):
        # User1 should be able to see Org1 details
        url = reverse('organisation-detail', kwargs={'orgId': self.org1.orgId})
        access_token = create_access_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], "John's Organisation")

        # User1 should not be able to see Org2 details
        url = reverse('organisation-detail', kwargs={'orgId': self.org2.orgId})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_organisation(self):
        # User1 should be able to create a new organisation
        url = reverse('organisation-list')
        access_token = create_access_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        data = {
            'name': "New Organisation",
            'description': "New Organisation Description",
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], "New Organisation")

    def test_add_user_to_organisation(self):
        # User1 should be able to add User2 to Org1
        url = reverse('add_user_to_organisation', kwargs={'orgId': self.org1.orgId})
        access_token = create_access_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        data = {
            'userId': str(self.user2.userId),
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "User added to organisation successfully")

        # User1 should not be able to add User2 to Org2
        url = reverse('add_user_to_organisation', kwargs={'orgId': self.org2.orgId})
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_access(self):
        # Ensure User2 cannot access Org1 details
        url = reverse('organisation-detail', kwargs={'orgId': self.org1.orgId})
        access_token = create_access_token(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Ensure User2 cannot create a new organisation
        url = reverse('organisation-list')
        data = {
            'name': "Another Organisation",
            'description': "Another Organisation Description",
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
