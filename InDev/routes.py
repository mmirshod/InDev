from InDev import app, db
from flask import render_template, redirect, url_for, flash
from InDev.forms import RegisterForm, LoginForm, PostForm, EditPostForm, UpdateDevForm
from InDev.models import Developer, Post
from flask_login import login_user, logout_user, login_required, current_user


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET", "POST"])
@app.route('/home/', methods=["GET", "POST"])
def about():
    return render_template('home.html')


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
@app.route('/sign-in/', methods=['GET', 'POST'])
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
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('about'))


@app.route('/blog')
def blog_page():
    posts = Post.query.order_by(Post.date_added)

    return render_template('blog/blog.html', posts=posts)


@app.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    temp = post
    form = EditPostForm()

    if form.validate_on_submit():
        post.title = temp.title
        post.content = form.content.data
        post.author_id = temp.author_id

        db.session.add(post)
        db.session.commit()

        flash("Post was edited successfully!", category='info')
        return redirect(url_for('blog_page'))

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While Editing post occurred error: {err_msg}', category='danger')
        return redirect(url_for('blog_page'))

    return render_template('blog/edit-post.html', form=form, post=post)


@app.route('/blog/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        # Author
        author = current_user.id
        # Creating 'Post' object
        post = Post(title=form.title.data, content=form.content.data, author_id=author)

        # Add to database
        db.session.add(post)
        db.session.commit()
        # Flask message:
        flash("New Post has been added!", category='info')
        return redirect(url_for('blog_page'))

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While creating new post occurred error: {err_msg}', category='danger')

    return render_template('blog/add_post.html', form=form)


@app.route('/blog/<int:post_id>')
def post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)


@app.route('/blog/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        flash("Post has been Deleted", category='info')
        return redirect(url_for('blog_page'))

    except:
        flash('Error! There was a problem with deleting post.')
        return redirect(url_for('blog_page'))


@app.route('/pricing')
@app.route('/pricing/')
def coming_soon():
    return render_template('errors/coming_soon.html')


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
    temp = dev_to_update
    form = UpdateDevForm()

    if form.validate_on_submit():
        dev_to_update.first_name = form.first_name.data
        dev_to_update.last_name = form.last_name.data
        dev_to_update.username = form.username.data
        dev_to_update.email_address = temp.email_address
        dev_to_update.password_hash = temp.password_hash
        dev_to_update.budget = temp.budget
        dev_to_update.date_added = temp.date_added

        db.session.add(dev_to_update)
        db.session.commit()

        flash("Account was edited successfully!", category='info')
        return redirect(url_for('team'))

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'While Editing account occurred error: {err_msg}', category='danger')
        return redirect(url_for('team'))

    return render_template('update-dev.html',
                           dev_to_update=dev_to_update, form=form, dev_id=dev_id)

# test
