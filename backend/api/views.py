from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter


from recipe.models import Tag, Recipe, Ingredient
from api.serializers import TagSerializer, RecipeSerializer, IngredientSerializer
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from django.shortcuts import get_object_or_404


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для жанров."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для жанров."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name')
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)




# class FollowViewSet(CreateModelMixin, ListModelMixin,
#                     GenericViewSet):
#     serializer_class = FollowSerializer
#     # permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
#     filter_backends = (SearchFilter,)
#     search_fields = ('=user__username', '=following__username')

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def get_queryset(self):
#         return self.request.user.follower