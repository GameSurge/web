import pysrvx
from flask import _app_ctx_stack, current_app


class SrvX:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def __repr__(self):
        if not hasattr(_app_ctx_stack.top, 'srvx_conn'):
            return '<SrvX()>'
        else:
            conn = self.conn
            return '<SrvX({}:{}, {})>'.format(conn.host, conn.port, conn.auth_user)

    def init_app(self, app):
        app.config.setdefault('SRVX_HOST', '127.0.0.1')
        app.config.setdefault('SRVX_PORT', 7702)
        app.config.setdefault('SRVX_BIND', None)
        app.config.setdefault('SRVX_PASSWORD', '')
        app.config.setdefault('SRVX_AUTHSERV_USERNAME', '')
        app.config.setdefault('SRVX_AUTHSERV_PASSWORD', '')
        app.teardown_appcontext(self.teardown)

    def connect(self):
        cfg = current_app.config
        return pysrvx.SrvX(
            host=cfg['SRVX_HOST'], port=cfg['SRVX_PORT'], bind=cfg['SRVX_BIND'], password=cfg['SRVX_PASSWORD'],
            auth_user=cfg['SRVX_AUTHSERV_USERNAME'], auth_password=cfg['SRVX_AUTHSERV_PASSWORD']
        )

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'srvx_conn'):
            ctx.srvx_conn.disconnect()

    @property
    def conn(self) -> pysrvx.SrvX:
        ctx = _app_ctx_stack.top
        if ctx is None:
            raise RuntimeError('Working outside of application context.')
        if not hasattr(ctx, 'srvx_conn'):
            ctx.srvx_conn = self.connect()
        return ctx.srvx_conn

    @property
    def authserv(self):
        return pysrvx.AuthServ(self.conn)

    @property
    def chanserv(self):
        return pysrvx.ChanServ(self.conn)

    @property
    def opserv(self):
        return pysrvx.OpServ(self.conn)


srvx = SrvX()
