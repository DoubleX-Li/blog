from collections import OrderedDict
from datetime import datetime

import markdown
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.login import current_user

from application import db
from application.main.forms import PostForm, CommentForm
from application.models import Post, Comment, User
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


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        email = form.email.data
        content = form.content.data
        comment_time = datetime.utcnow()
        comment = Comment(email=email, content=content, comment_time=comment_time, post_id=post_id)
        db.session.add(comment)
        return redirect(url_for('.post', post_id=post_id))
    post = Post.query.get(post_id)
    comments = Comment.query.filter_by(post_id=post_id)
    return render_template('post.html', post=post, form=form, comments=comments, User=User)


@main.route('/archives', methods=['GET'])
def archives():
    posts = Post.query.all()
    years = []
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    result = OrderedDict()
    for post in posts:
        if str(post.post_time.year) not in years:
            years.append(str(post.post_time.year))

    for year in years:
        result[year] = OrderedDict()
        for month in months:
            result[year][month] = []

    for post in posts:
        result[str(post.post_time.year)][str(post.post_time.month)].append(post)

    category = OrderedDict()
    for year in result:
        category[year] = OrderedDict()
        for month in result[year]:
            if len(result[year][month]) != 0:
                category[year][month] = result[year][month]
    print(category)
    return render_template('archives.html',category=category)
