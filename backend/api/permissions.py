from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)

METHODS = ('PATCH', 'DELETE')


class RecipePermissions(IsAuthenticatedOrReadOnly):
    """
    A class that defines that only the author can PATCH or DELETE a recipe.
    For the rest of the requests, the IsAuthenticatedOrReadOnly class works.
    """

    def has_object_permission(self, request, view, obj):
        print(f'obj = {obj}')
        if request.method in METHODS:
            return (obj.author == request.user)
        return super().has_object_permission(request, view, obj)


class IsAuthor(IsAuthenticated):
    """A class that defines that only the author can make changes."""

    def has_object_permission(self, request, view, obj):
        print('has obj perm')
        if request.user.is_authenticated:
            return request.user == obj.user
        return super().has_object_permission(request, view, obj)
