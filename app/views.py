import bcrypt
import hmac
from datetime import datetime
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, EditUserForm, NewTaskForm, SearchForm, RegisterForm, EditTaskForm
from .models import User, Task
from .emails import follower_notification
from config import TASKS_PER_PAGE, MAX_SEARCH_RESULTS

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_login = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@app.route('/tasks', methods=['GET', 'POST'])
@app.route('/tasks/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = NewTaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, mod_date=datetime.utcnow(), create_date=datetime.utcnow(), user=g.user, blocks=form.blocks.data, blocked_by=form.blocked_by.data)
        db.session.add(task)
        db.session.commit()
        flash('Task added')
        return redirect(url_for('index'))
    tasks = g.user.open_tasks.paginate(page, TASKS_PER_PAGE, False)
    return render_template('tasks.html', title = 'Tasks', form=form, tasks=tasks)

@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edituser():
    form = EditUserForm(obj=g.user)
    if form.validate_on_submit():
        g.user.email = form.email.data
        g.user.name = form.name.data
        g.user.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    return render_template('edituser.html', form = form)

@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = g.user.tasks.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query = query,
                           results = results)

@app.route('/user/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember = form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if (hmac.compare_digest(bcrypt.hashpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')), user.password.encode('utf-8'))):
                login_user(user)
                return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title = 'Sign In', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/profile')
@login_required
def user():
    return render_template('user.html', user=g.user)

@app.route('/task/<int:id>')
@login_required
def task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        flash('Task %d not found.' % id)
        return redirect(url_for('index'))
    if task.user_id != g.user.id:
        flash('This task is owned by a different user.')
        return redirect(url_for('index'))
    return render_template('task.html', task=task)

@app.route('/task/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        flash('Task %d doesn\'t exist.' % id)
        return redirect(url_for('index'))
    if task.user_id != g.user.id:
        flash('This task is owned by a different user.')
        return redirect(url_for('index'))
    form = EditTaskForm(obj=task)
    form.blocks.query = g.user.tasks.filter(Task.id!=id).order_by(Task.name)
    form.blocked_by.query = g.user.tasks.filter(Task.id!=id).order_by(Task.name)
    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        flash('Changes saved.')
        return redirect(url_for('task', id=task.id))
    return render_template('edittask.html', form=form, task=task)

@app.route('/task/done/<int:id>', methods=['GET', 'POST'])
@login_required
def complete_task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        flash('Task %d doesn\'t exist.' % id)
        return redirect(url_for('index'))
    if task.user_id != g.user.id:
        flash('This task is owned by a different user.')
        return redirect(url_for('index'))
    task.done = True
    task.completed_date = datetime.utcnow()
    db.session.commit()
    flash('Task Completed.')
    return redirect(url_for('index'))

@app.route('/task/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        flash('Task %d doesn\'t exist.' % id)
        return redirect(url_for('index'))
    if task.user_id != g.user.id:
        flash('This task is owned by a different user.')
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.')
    return redirect(url_for('index'))

@app.route('/history')
@app.route('/history/<int:page>')
@login_required
def history(page=1):
    tasks = Task.query.filter(Task.user_id==g.user.id, Task.done==True).order_by(Task.completed_date.desc()).paginate(page, TASKS_PER_PAGE, False)
    return render_template('history.html', tasks=tasks)

