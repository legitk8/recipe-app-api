"""
Tests for Tag APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


class PublicTagAPITests(TestCase):
    """Test the publicly available Tag API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test the authorized user Tag API."""

    def setUp(self):
        self.client = APIClient()

        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Meat')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user."""
        user2 = create_user(email='test2@example.com', password='test@123')
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Meat')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_update_tag(self):
        """Test updating tags."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        payload = {'name': 'Veg'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting tags."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        tag = Tag.objects.filter(id=tag.id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(tag.exists())
