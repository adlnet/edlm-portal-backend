from rest_framework import permissions


class CustomObjectPermissions(permissions.DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    VIEW_PERMS = '%(app_label)s.view_%(model_name)s'

    perms_map = {
        'GET': [VIEW_PERMS],
        'OPTIONS': [VIEW_PERMS],
        'HEAD': [VIEW_PERMS],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
