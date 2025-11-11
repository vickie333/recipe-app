"""
Serializers for Recipe APIs
"""

from rest_framework import serializers
from app.models import Recipe
from app.models import Tag, Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe object"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['title', 'id', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, recipe, tags_data):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag_data in tags_data:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag_data)
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe"""
        tags_data = validated_data.pop('tags', []) #it removes tags from validated_data
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags_data)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags_data = validated_data.pop('tags', None)

        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

