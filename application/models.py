import hashlib
import random
from datetime import datetime

import markdown
from flask import current_app
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from application import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    about_me = db.Column(db.String(140))
    last_login = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def ping(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def name(id):
        return User.query.get(id).username

    @staticmethod
    def gravatar(size=100, email=email, default='identicon', rating='g'):
        url = 'https://cdn.v2ex.com/gravatar'
        hash = hashlib.md5(email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


pt = db.Table('pt',
              db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
              db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
              )


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    img = db.Column(db.String(255))
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    post_time = db.Column(db.DateTime)
    alt_time = db.Column(db.DateTime)
    last_comment_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    tags = db.relationship('Tag', secondary=pt)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            p = Post(title=forgery_py.lorem_ipsum.sentence(),
                     content=forgery_py.lorem_ipsum.sentence(),
                     post_time=forgery_py.date.date(),
                     user_id=1)

            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        target.content_html = markdown.markdown(value, extensions=[
            'fenced_code',
            'codehilite(css_class=codehilite)',
            'toc',
            'tables',
            'sane_lists',
        ])

    def notExistTag(self, tag_name):
        tag = Tag.query.filter_by(tag_name=tag_name).first()
        if tag:
            return False
        return True

    def postDontHaveTag(self, tag):
        if tag in self.tags:
            return False
        else:
            return True

    def addTag(self, tag_name):
        if self.notExistTag(tag_name):
            tag = Tag(tag_name)
        else:
            tag = Tag.query.filter_by(tag_name=tag_name).first()
        if self.postDontHaveTag(tag):
            self.tags.append(tag)

    def __repr__(self):
        return "<Post: %r>" % self.title

db.event.listen(Post.content, 'set', Post.on_changed_content)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    content = db.Column(db.Text)
    comment_time = db.Column(db.DateTime)
    author_name = db.Column(db.String(120))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            c = Comment(email=forgery_py.internet.email_address(),
                        content=forgery_py.lorem_ipsum.sentence(),
                        comment_time=forgery_py.date.date(),
                        post_id=random.randint(1, 104))

            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(64), unique=True)

    posts = db.relationship('Post', secondary=pt)

    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __repr__(self):
        return '<Tag %r>' % (self.tag_name)
