"""
Serializers for Recipe APIs
"""

from rest_framework import serializers
from app.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe object"""
    class Meta:
        model = Recipe
        fields = ['title', 'id', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']
