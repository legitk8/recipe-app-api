"""
Serializer for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe objects."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        user = self.context['request'].user

        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=user, **tag)
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details."""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description']
