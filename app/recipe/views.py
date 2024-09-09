"""
Views for Recipe API.
"""
from rest_framework import (
    viewsets,
    mixins
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer, IngredientSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipe for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for the request."""
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe with the authenticated user."""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """View to manage Tag APIs."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """View to manage ingredient APIs."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve ingredients for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
