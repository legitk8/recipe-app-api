"""
Tests for Recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a new Recipe instance."""
    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': Decimal(10.5),
        'description': 'Test Recipe Description',
        'link': 'https://www.example.com',
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the publicly available Recipe API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the private recipe API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
            name='Test User',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user."""
        user2 = get_user_model().objects.create_user(
            email='test2@example.com',
            password='test456',
            name='Test User2',
        )

        create_recipe(self.user)
        create_recipe(user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail."""
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe."""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 10,
            'price': Decimal(10.5),
            'description': 'Test Recipe Description',
            'link': 'https://www.example.com',
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(self.user, recipe.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch."""
        recipe_link = 'https://www.example.com/recipe.pdf'
        recipe = create_recipe(
            self.user,
            title='Test Recipe',
            time_minutes=10,
            price=Decimal(10.5),
            link=recipe_link,
        )

        url = detail_url(recipe.id)

        payload = {'title': 'Updated Title'}
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, recipe_link)
        self.assertEqual(self.user, recipe.user)

    def test_full_update_recipe(self):
        """Test updating a recipe with patch."""
        recipe = create_recipe(
            self.user,
            title='Test Recipe',
            time_minutes=10,
            price=Decimal(10.5),
        )

        url = detail_url(recipe.id)

        payload = {
            'title': 'Updated Title',
            'time_minutes': 11,
            'price': Decimal(12.5),
        }
        res = self.client.put(url, payload)

        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user, recipe.user)

    def test_create_recipe_with_new_tags(self):
        """Test creating a new recipe with new tags."""
        payload = {
            'title': 'Hakka Noodles',
            'time_minutes': 10,
            'price': Decimal(10.5),
            'description': 'Test Recipe Description',
            'link': 'https://www.example.com',
            'tags': [{'name': 'Chinese'}, {'name': 'Veg'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        recipes = Recipe.objects.filter(user=self.user)
        tags = Tag.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes.first()
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()

            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a new recipe with existing tags."""
        chinese_tag = Tag.objects.create(name='Chinese', user=self.user)
        payload = {
            'title': 'Hakka Noodles',
            'time_minutes': 10,
            'price': Decimal(10.5),
            'description': 'Test Recipe Description',
            'link': 'https://www.example.com',
            'tags': [{'name': 'Chinese'}, {'name': 'Veg'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        recipes = Recipe.objects.filter(user=self.user)
        tags = Tag.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes.first()
        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(chinese_tag, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()

            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a new tag on a recipe update."""
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)

        payload = {'tags': [{'name': 'Veg'}]}
        res = self.client.patch(url, payload, format='json')

        tag = Tag.objects.get(user=self.user, name='Veg')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, 'Veg')
        self.assertIn(tag, recipe.tags.all())

    def test_assign_tag_on_update(self):
        """Test updating recipe with an existing tag."""
        tag_veg = Tag.objects.create(name='Veg', user=self.user)
        tag_non_veg = Tag.objects.create(name='Non-Veg', user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag_veg)

        url = detail_url(recipe.id)
        payload = {'tags': [{'name': 'Non-Veg'}]}
        res = self.client.patch(url, payload, format='json')

        tags = Tag.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertIn(tag_non_veg, recipe.tags.all())
        self.assertNotIn(tag_veg, recipe.tags.all())

    def test_clear_recipe_tags_on_update(self):
        """Test clearing recipe tags."""
        tag = Tag.objects.create(name='Veg', user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag)

        url = detail_url(recipe.id)
        payload = {'tags': []}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a new recipe with new ingredients."""
        payload = {
            'title': 'Hakka Noodles',
            'time_minutes': 10,
            'price': Decimal(10.5),
            'description': 'Test Recipe Description',
            'link': 'https://www.example.com',
            'ingredients': [{'name': 'Noodles'}, {'name': 'Soy Sauce'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        recipes = Recipe.objects.filter(user=self.user)
        ingredients = Ingredient.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes.first()
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a new recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(
            name='Soy Sauce',
            user=self.user
        )

        payload = {
            'title': 'Hakka Noodles',
            'time_minutes': 10,
            'price': Decimal(10.5),
            'description': 'Test Recipe Description',
            'link': 'https://www.example.com',
            'ingredients': [{'name': 'Soy Sauce'}, {'name': 'Salt'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        recipes = Recipe.objects.filter(user=self.user)
        ingredients = Ingredient.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes.first()
        self.assertEqual(recipe.ingredients.count(), 2)

        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()

            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating a new ingredient on recipe update."""
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)

        payload = {'ingredients': [{'name': 'Soy Sauce'}]}
        res = self.client.patch(url, payload, format='json')

        ingredient = Ingredient.objects.get(user=self.user, name='Soy Sauce')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_assign_ingredient_on_update(self):
        """Test assigning an existing ingredient on recipe update."""
        ingredient_salt = Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )
        ingredient_sugar = Ingredient.objects.create(
            user=self.user,
            name='Sugar'
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_salt)

        url = detail_url(recipe.id)

        payload = {'ingredients': [{'name': 'Sugar'}]}
        res = self.client.patch(url, payload, format='json')

        ingredients = Ingredient.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertIn(ingredient_sugar, recipe.ingredients.all())
        self.assertNotIn(ingredient_salt, recipe.ingredients.all())

    def test_clear_ingredients_on_update(self):
        """Test clearing ingredients on update."""
        ingredient_salt = Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_salt)

        url = detail_url(recipe.id)

        payload = {'ingredients': []}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
