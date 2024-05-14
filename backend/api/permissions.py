from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS
)


class AuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    '''
    Checking the access rights to the object.
    The user has access if he is the author of the object,
    only reading is allowed.
    '''

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
