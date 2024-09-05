"""
Views for Recipe API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage Recipe APIs."""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipe for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
