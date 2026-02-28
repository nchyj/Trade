from flask import Flask
from flask_cors import CORS

from .api.routes import api_bp
from .config import Config
from .db import Base, init_db


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    CORS(app)

    engine = init_db(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(bind=engine)

    app.register_blueprint(api_bp)
    return app
