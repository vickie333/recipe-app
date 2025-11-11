"""Test for ingredient API."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from app.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_id(ingredient_id):
    """Create and return an ingredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email='user@example.com', password='testpass'):
    """Create a user for testing."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access the endpoint."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user."""
        other_user = create_user(email='other@example.com', password='otherpass123')
        Ingredient.objects.create(user=other_user, name='Pepper')
        ingredient = Ingredient.objects.create(user=self.user, name='Cumin')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}
        url = detail_id(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Turmeric')

        url = detail_id(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(id=ingredient.id)
        self.assertFalse(ingredients.exists())