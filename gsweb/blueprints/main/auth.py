from flask import current_app, flash, redirect, render_template, url_for, request
from flask_login import login_user, logout_user
from werkzeug.utils import cached_property
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError

from gsweb import db, srvx
from gsweb.blueprints.main import bp
from gsweb.models.users import User
from gsweb.util.forms import Form


class LoginForm(Form):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    @cached_property
    def _checkpass_result(self):
        return srvx.authserv.checkpass(self.username.data, self.password.data, verbose=True)

    def validate_username(self, field):
        if not field.data or self._checkpass_result['valid']:
            return
        if self._checkpass_result['reason'] == 'invalid_account':
            raise ValidationError('No such account')

    def validate_password(self, field):
        if not field.data or self._checkpass_result['valid']:
            return
        if self._checkpass_result['reason'] == 'invalid_password':
            raise ValidationError('Invalid password')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.from_srvx_account(form.username.data)
        db.session.commit()
        login_user(user, remember=True)
        current_app.logger.getChild('auth').info('User %r logged in from %s', user, request.remote_addr)
        flash('Login successful')
        # TODO: use a `next` argument to get back to the previous page.
        return redirect(url_for('.index'))
    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Logout successful')
    return redirect(url_for('.index'))
