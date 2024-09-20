"""
Tests for models.
"""
import os
from decimal import Decimal

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        sample_emails = [
            ['test1@example.com', 'test1@example.com'],
            ['test2@EXAMPLE.COM', 'test2@example.com'],
            ['Test3@Example.com', 'Test3@example.com'],
            ['TEST4@example.com', 'TEST4@example.com'],
            ['test5@example.COM', 'test5@example.com'],
            ['Test6@example.com', 'Test6@example.com'],
        ]

        for email, normalized_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='test123'
            )
            self.assertEqual(user.email, normalized_email)

    def test_new_user_email_blank(self):
        """Test that creating user with no email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='test123'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a new recipe."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test@123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Test recipe',
            time_minutes=5,
            price=Decimal(1.5),
            description='Test recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_tag_model(self):
        """Test the tag model."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Vegan')

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_model(self):
        """Test the ingredient model."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Test ingredient',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_media_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(
            file_path,
            os.path.join('uploads', 'recipe', f'{uuid}.jpg')
        )
