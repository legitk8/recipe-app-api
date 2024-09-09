"""
Tests for Ingredient APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


class PublicIngredientApiTests(TestCase):
    """Test the publicly available Ingredient API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the private Ingredient API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Wheat')
        Ingredient.objects.create(user=self.user, name='Chicken')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test ingredients returned are for authenticated user."""
        user2 = create_user(email='test2@example.com')
        Ingredient.objects.create(user=user2, name='Wheat')
        ingredient = Ingredient.objects.create(user=self.user, name='Chicken')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], ingredient.id)
        self.assertEqual(res.data[0]['name'], ingredient.name)
