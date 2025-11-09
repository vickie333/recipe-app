"""
Serializers for Recipe APIs
"""

from rest_framework import serializers
from app.models import Recipe
from app.models import Tag

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe object"""
    class Meta:
        model = Recipe
        fields = ['title', 'id', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']