import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_login import LoginManager
from flask_restful import Resource, Api


def create_app():
    new_app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Staring Local Development")
        new_app.config.from_object(LocalDevelopmentConfig)
    db.init_app(new_app)

    api = Api(new_app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(new_app)

    from application.models import User

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    new_app.app_context().push()
    return new_app, api


app, api = create_app()

# Import all the controllers so they are loaded
# Add all the resful controllers
from application.api import *
from application.controllers import *

api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")
api.add_resource(PostAPI, "/api/post", "/api/post/<int:postId>")

if __name__ == '__main__':
    # Run the Flask app
    db.create_all()
    app.run(host='0.0.0.0', port=8080)
