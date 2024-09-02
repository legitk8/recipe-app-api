"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


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
