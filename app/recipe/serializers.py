"""
Serializer for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe objects."""

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
        ]
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details."""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description']
