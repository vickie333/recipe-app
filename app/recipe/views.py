"""
Views for the Recipe API
"""

from rest_framework import generics

from recipe.serializers import RecipeSerializer

class CreateRecipeView(generics.CreateAPIView):
    """View for the Recipe API"""
    serializer_class = RecipeSerializer