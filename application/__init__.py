from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)

    # if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
    #     from flask.ext.sslify import SSLify
    #     sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # from .api import api as api_1_0_blueprint
    # app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    @app.template_filter('part_text')
    def part_text_filter(s):
        return s[0:100]

    from .models import User
    from .models import Post
    @app.template_filter('author_name')
    def author_name_filter(id):
        user = User.query.get(id)
        return user.username

    @app.template_filter('author_avatar')
    def author_avatar_filter(id):
        user = User.query.get(id)
        return User.gravatar(email=user.email)

    @app.template_filter('author_about')
    def author_about_filter(id):
        user = User.query.get(id)
        return user.about_me

    @app.template_filter('post_title')
    def post_title_filter(id):
        post = Post.query.get(id)
        return post.title

    @app.template_filter('avatar')
    def avatar_filter(email):
        avatar = User.gravatar(email=email)
        return avatar

    app.jinja_env.filters['part_text'] = part_text_filter
    app.jinja_env.filters['author_name'] = author_name_filter
    app.jinja_env.filters['author_avatar'] = author_avatar_filter
    app.jinja_env.filters['author_about'] = author_about_filter
    app.jinja_env.filters['post_title'] = post_title_filter
    app.jinja_env.filters['avatar'] = avatar_filter

    return app
