from aiohttp import web
from app.config import Config
from app.cleanups import close_db
from app.models import db
from app.startups import init_db
from app.api.routes import add_routes


app = web.Application()
app['db'] = db


def init_app() -> web.Application:
    app['config'] = Config

    # Startups
    app.on_startup.append(init_db)

    # Cleanups
    app.on_cleanup.append(close_db)
    add_routes(app)

    return app
