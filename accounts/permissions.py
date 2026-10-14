"""Authorization decorators for role-based access control."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionsDenied


def role_required(*roles):
    """Allow access only to signed-in users whose role is in 'roles'."""

    def decorator(view_func):
        """Wrap a view with authentication and role validation."""

        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            """Execute the view only when the current user has an allowed role."""

            if request.user.role not in roles:
                raise PermissionsDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
