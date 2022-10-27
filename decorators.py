from functools import wraps
# from requests import *
from flask import request
from flask import current_app
from flask_login import current_user


def admin_only(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # request.method in EXEMPT_METHODS or
        if current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not (current_user.is_authenticated and current_user.is_admin):
            return current_app.login_manager.unauthorized()

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)


    return decorated_view