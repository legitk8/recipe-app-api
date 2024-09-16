"""
Serializer for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient objects."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe objects."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
            'ingredients',
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, instance):
        """Handle tag creating or fetching."""
        user = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=user, **tag)
            instance.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, instance):
        """Handle ingredient creating or fetching."""
        user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=user,
                **ingredient
            )
            instance.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, instance)
        self._get_or_create_ingredients(ingredients, instance)
        return instance

    def update(self, instance, validated_data):
        """Update a recipe."""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details."""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description']
