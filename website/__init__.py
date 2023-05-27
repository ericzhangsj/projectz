from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    from .views import views
    from .log import log

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(log, url_prefix = '/')

    from .models import User, Post
    
    loginManager = LoginManager()
    loginManager.login_view = 'views.explore'
    loginManager.init_app(app)
    from .models import User

    @loginManager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)

    return app



def create_database(app):
    if not path.exists('website' + DB_NAME):
        with app.app_context():
            db.create_all() 
            print('Database has been created!')
