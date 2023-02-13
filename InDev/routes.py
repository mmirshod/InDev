# *********************************** Import modules ***************************************

from InDev import app, db
from flask import render_template, redirect, url_for, flash, request
from InDev.forms import RegisterForm, LoginForm, PostForm, EditPostForm, UpdateDevForm, SearchForm
from InDev.models import Developer, Post
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# *********************************** Context Processor **************************************

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/pricing')
@app.route('/pricing/')
def coming_soon():
    return render_template('errors/coming_soon.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    posts = Post.query

    if form.validate_on_submit():
        post_searched = form.searched.data
        posts = posts.filter(Post.content.like('%' + post_searched + '%'))
        posts = posts.order_by(Post.title).all()
        size = len(posts)

        return render_template('search-page.html',
                               form=form,
                               searched=post_searched,
                               posts=posts,
                               size=size)

# ************************************* Error Pages *******************************************


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# ************************************* Main Pages **********************************************


@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def about():
    return render_template('services.html')


@app.route('/services')
def services_page():
    return render_template('services.html')


# ************************ Authentication ***************************************************

@app.route('/sign-up', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = Developer(first_name=form.first_name.data,
                                   last_name=form.last_name.data,
                                   username=form.username.data,
                                   email_address=form.email_address.data,
                                   password=form.password1.data
                                   )
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as {user_to_create.username}', category='success')

        return redirect(url_for('about'))
    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While Creating Developer Account occurred error: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/sign-in', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Developer.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('about'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('about'))


# *********************************** Blog Section *********************************************

@app.route('/blog')
def blog_page():
    posts = Post.query.order_by(Post.date_added)

    return render_template('blog/blog.html', posts=posts)


@app.route('/blog/<int:post_id>')
def post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)


@app.route('/blog/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if request.method == 'POST':
        # Who posted:
        author = current_user.id
        post = Post(
            title=request.form['title'],
            content=request.form['content'],
            author_id=author,
            pic=request.files['pic']
        )
        # Grab Image Name
        pic_filename = secure_filename(post.pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
        # Tool to save image
        saver = request.files['pic']
        # Change filename to a string to store in DB
        post.pic = pic_name
        # Add to DB
        db.session.add(post)
        db.session.commit()
        # Save image to server
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        # Flash message
        flash('New Post added successfully', category='success')
        return redirect(url_for('blog_page'))

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While creating new post occurred error: {err_msg}', category='danger')

    return render_template('blog/add_post.html', form=form)


@app.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm()
    if current_user.id == post.author_id:
        if request.method == 'POST':
            post.content = request.form['content']
            post.pic = request.files['pic']
            # Grab image
            pic_filename = secure_filename(post.pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + '_' + pic_filename
            # Convert to str to store in DB
            post.pic = pic_name
            # Tool to save to server
            saver = request.files['pic']
            # Add to DB:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # Flash message
            flash("Post has been edited successfully")
            return redirect(url_for('blog_page'))

        if form.errors != {}:  # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(f'While Editing post occurred error: {err_msg}', category='danger')
            return redirect(url_for('blog_page'))

        return render_template('blog/edit-post.html', form=form, post=post)
    else:
        flash('Error! You are not authorized to edit this post.', category='danger')
        return redirect(url_for('blog_page'))


@app.route('/blog/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if current_user.id == post_to_delete.author_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Post has been Deleted", category='info')
            return redirect(url_for('blog_page'))

        except:
            flash('Error! There was a problem with deleting post.', category='danger')
            return redirect(url_for('blog_page'))
    else:
        flash('Error! You are not authorized to delete this post.', category='danger')
        return redirect(url_for('blog_page'))


# ********************************** Developers Section ***************************************

@app.route('/team')
def team():
    devs = Developer.query.all()

    return render_template('developers.html', devs=devs)


@app.route('/team/<int:dev_id>')
@login_required
def developer_page(dev_id):  # dev_id -> Developer id
    developer = Developer.query.get_or_404(dev_id)

    return render_template('developer-page.html', developer=developer)


@app.route('/team/<int:dev_id>/update', methods=['GET', 'POST'])
@login_required
def update_dev_info(dev_id):
    dev_to_update = Developer.query.get_or_404(dev_id)
    form = UpdateDevForm()

    if request.method == 'POST':
        dev_to_update.first_name = request.form['first_name']
        dev_to_update.last_name = request.form['last_name']
        dev_to_update.username = request.form['username']
        dev_to_update.profile_pic = request.files['profile_pic']
        # Grab Image Name
        pic_filename = secure_filename(dev_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
        # Save that image
        saver = request.files['profile_pic']
        # Change to a string to store in db
        dev_to_update.profile_pic = pic_name

        db.session.commit()
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        flash("Account was edited successfully!", category='info')
        return redirect(url_for('team'))

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While Editing account occurred error: {err_msg}', category='danger')
        return redirect(url_for('team'))

    return render_template('update-dev.html',
                           dev_to_update=dev_to_update,
                           form=form,
                           dev_id=dev_id
                           )


@app.route('/delete/<int:dev_id>')
@login_required
def delete_dev(dev_id):
    dev = Developer.query.get_or_404(dev_id)
    if current_user.id == dev_id or current_user.id == 1:
        db.session.delete(dev)
        db.session.commit()

        flash(f"Account {dev.username} was deleted", category='info')
        if current_user.id == dev_id:
            logout_user()
            return redirect(url_for('about'))
        else:
            return redirect(url_for('team'))

    else:
        flash("You are not authorized or do not have enough rights to delete this user", category='warning')
        return redirect(url_for('team'))


@app.route('/delete-profile-pic/<int:dev_id>')
def delete_profile_pic(dev_id):
    dev = Developer.query.get_or_404(dev_id)
    dev.profile_pic = 'default-pic.svg'
    db.session.commit()
    return redirect(url_for('developer_page', dev_id=dev_id))


# ************************************* Clients Section **************************************
