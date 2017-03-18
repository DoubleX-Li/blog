from collections import OrderedDict
from datetime import datetime

import markdown
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask.ext.login import current_user
from flask.ext.login import login_required

from application import db
from application.main.forms import PostForm, CommentForm
from application.models import Post, Comment, User, Tag
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
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tag_names = form.new_tag.data
        post_time = datetime.utcnow()
        post = Post(title=title, content=content, post_time=post_time, user_id=current_user.id)
        for tag_name in tag_names.split(','):
            post.addTag(tag_name)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('.index'))
    return render_template('add_post.html', form=form)


@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.remove(post)
    db.session.commit()
    return redirect(url_for('.index'))


@main.route('/alt_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def alt_post(post_id):
    post = Post.query.get(post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        tag_names = form.new_tag.data
        post.content = form.content.data
        for tag_name in tag_names.split(','):
            post.addTag(tag_name)
        db.session.add(post)
        db.session.commit()
        post.alt_time = datetime.utcnow()

        if post:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.post', post_id=post_id))
        else:
            flash('修改文章出了问题')
    else:
        # GET请求时，处理form的tittle和content数据，以免传递post
        form.title.data = post.title
        form.content.data = post.content
        new_tag_str = ''
        for i, tag in enumerate(post.tags):
            new_tag_str += tag.tag_name
            if i < len(post.tags) - 1:
                new_tag_str += ','
        form.new_tag.data = new_tag_str
        print(new_tag_str)
    return render_template('add_post.html',
                           title=post.title,
                           form=form)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    page = request.args.get('page', 1, type=int)
    if page:
        form = CommentForm()
        post = Post.query.get(post_id)
    else:
        flash('没有找到文章')
        return redirect('main.index')
    if form.validate_on_submit():
        email = form.email.data
        content = form.content.data
        comment_time = datetime.utcnow()
        comment = Comment(email=email, content=content, comment_time=comment_time, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('成功添加评论')

        # 将新评论发送给管理员
        from application.email import send_email
        author = User.query.get(1)
        to_address = author.email
        send_email(to_address, '新的评论', 'auth/email/new_comment', user=author, post=post, comment=comment)
        return redirect(url_for('.post', post_id=post_id, _anchor='add-comment'))

    pagination = Comment.query.filter_by(post_id=post_id).order_by(Comment.comment_time.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, form=form, comments=comments, User=User, pagination=pagination)


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
    tags = Tag.query.all()
    return render_template('archives.html', category=category,tags=tags)


@main.route('/tag/<int:tag_id>')
def tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        posts = tag.posts
        post_num = len(list(posts))
        return render_template('tag.html',
                               title=tag.tag_name,
                               tag=tag,
                               posts=posts,
                               post_num=post_num)
    else:
        flash('获取标签页面失败')
        return redirect(url_for('index'))


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/mail')
def mail():
    """test email function"""
    from application.email import send_email
    to_address = User.query.get(1).email
    send_email(to_address, '测试', 'auth/email/test_email')
    message = "Done!"
    return render_template('email.html', message=message)

@main.route('/robots.txt')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])