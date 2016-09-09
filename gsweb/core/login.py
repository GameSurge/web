from flask_login import LoginManager, AnonymousUserMixin

from gsweb.models import User


class _AnonymousUser(AnonymousUserMixin):
    def __bool__(self):
        return False

    def __repr__(self):
        return '<AnonymousUser>'


login_manager = LoginManager()
login_manager.anonymous_user = _AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if not user or user.is_deleted:
        return None
    return user
