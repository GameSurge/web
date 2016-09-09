from flask import current_app
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr

from gsweb import db, srvx


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    @declared_attr
    def __table_args__(cls):
        return db.Index(None, db.func.lower(cls.name), unique=True, postgresql_where=db.text('NOT is_deleted')),

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # XXX: We do not store emails for accounts here.  While doing so
    # would allow us to re-associated an existing account here when
    # the srvx account expired and got re-registered by the same user
    # later (assuming they use the same email) but in srvx it's a new
    # account too.
    # OTOH, re-associating accounts by emails would allow us to better
    # keep track of a user's history (e.g. channels, trusts, etc.)...

    def __repr__(self):
        deleted = ', is_deleted=True' if self.is_deleted else ''
        return '<User({}, account_id={}{})>'.format(self.id, self.account_id, deleted)

    @classmethod
    def from_srvx_account(cls, account_name=None, *, account_id=None, allow_create=True):
        """Retrieve or create a user from a srvx account name/id.

        If a local user was found but has a different account name
        than the srvx account, the local account name will be updated
        accordingly.

        It is a good idea to call ``db.session.commit()`` after using
        this method, especially if ``allow_create`` is enabled.

        :param account_name: The name of the srvx account
        :param account_id: The ID of the srvx account (cannot be
                           combined with `account_name`)
        :param allow_create: Whether a new `User` should be created
                             if no existing one could be found.  The
                             newly created user will be added to the
                             sqlalchemy session and flushed to the
                             database.
        """
        if account_name and account_id:
            raise ValueError('account_name and account_id are mutually exclusive')
        elif account_name:
            data = srvx.authserv.accountinfo(account_name)
        elif account_id:
            data = srvx.authserv.accountinfo('#{}'.format(account_id))
        else:
            raise ValueError('account_name or account_id must be specified')
        # we expect the account to exist in srvx
        if not data:
            raise ValueError('Invalid account specified')
        # check whether we already know the user
        user = cls.query.filter_by(account_id=data['id']).one_or_none()
        if user:
            current_app.logger.debug('Found existing user %r', user)
            # we only flag accounts as deleted when they are deleted from srvx.
            # there should never be an account in the database that is deleted
            # but has a valid srvx account_id
            assert not user.is_deleted
            # synchronize the name in case the user was renamed in srvx
            if user.name != data['account']:
                current_app.logger.info('Updated account name of %r: %s', user, data['account'])
                user.name = data['account']
                db.session.flush()
            return user
        elif not allow_create:
            return None
        # XXX: this does not take irc-specific comparison rules such
        # as \ == | into account.  as long as we do not lookup users
        # using the name stored in the database this is not an issue.
        conflicting_user = (cls.query
                            .filter(db.func.lower(cls.name) == data['account'].lower(),
                                    ~cls.is_deleted)
                            .one_or_none())
        if conflicting_user:
            # there should never be a user with the same name but a different ID
            assert srvx.authserv.checkid(conflicting_user.account_id) is None
            # but in case an account was re-registered and we never checked it
            # we flag it as deleted now
            conflicting_user.is_deleted = True
            current_app.logger.info('Deleted user %r', conflicting_user)
            db.session.flush()
        # create a new user
        user = cls(account_id=data['id'], name=data['account'])
        db.session.add(user)
        db.session.flush()
        current_app.logger.info('Created new user %r', user)
        return user
