"""
Serializers for Recipe APIs
"""

from rest_framework import serializers
from app.models import Recipe, Tag, Ingredient

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
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['title', 'id', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, recipe, tags_data):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag_data in tags_data:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag_data)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, recipe, ingredients_data):
        """Handle getting or creating ingredients as needed"""
        auth_user = self.context['request'].user
        for ingredient_data in ingredients_data:
            ingredient_obj, created = Ingredient.objects.get_or_create(user=auth_user, **ingredient_data)
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe"""
        tags_data = validated_data.pop('tags', []) #it removes tags from validated_data
        ingredients_data = validated_data.pop('ingredients', []) #it removes ingredients from validated_data

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags_data)
        self._get_or_create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags_data)
        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(instance, ingredients_data)
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

