from datetime import datetime

import markdown
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.login import current_user

from application import db
from application.main.forms import PostForm
from application.models import Post
from manage import app
from . import main


@main.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.post_time.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get(post_id)
    return render_template('post.html', post=post)


@main.route('/posts/add', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        content = markdown.markdown(content, extensions=[
            'fenced_code',
            'codehilite(css_class=codehilite)',
            'toc',
            'tables',
            'sane_lists',
        ])
        post_time = datetime.utcnow()
        post = Post(title=title, content=content, post_time=post_time, user_id=current_user.id)
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('add_post.html', form=form)
