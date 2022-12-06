import os                 # os is used to get environment variables IP & PORT
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from models import Task, User
from models import Comment as Comment
from sqlalchemy.exc import NoResultFound
from forms import RegisterForm, LoginForm, CommentForm
from functools import wraps
import bcrypt

app = Flask(__name__)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'This is a secret'
db.init_app(app)

with app.app_context():
    db.create_all()

def requires_user_login(route_func):
    """Redirects to login page if not logged in"""
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            flash('Please login first')
            return redirect(url_for('login'))
        return route_func(*args, **kwargs)
    return wrapper
    
# runs if 404 error occurs (user typed a wrong url)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page does not exist"), 404

# runs if 405 error occurs (method not allowed)
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', message="Page does not exist"), 405

# runs if NoResultFound exception is raised (the url contained an invalid task id)
@app.errorhandler(NoResultFound)
def task_not_found(e):
    return render_template('error.html', message="Whoops, looks like that task does not exist"), 404
        
@app.route('/index/')
@app.route('/')
@requires_user_login
def index():
    return render_template("index.html", user=session['user'])

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        return redirect(url_for('get_tasks'))
        
    form = RegisterForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        h_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = {'first_name': new_user.first_name, 'last_name': new_user.last_name}
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_tasks'))
    else:
        return render_template('register.html', form=form)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if session.get('user'):
        return redirect(url_for('get_tasks'))

    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = {'first_name': the_user.first_name, 'last_name': the_user.last_name}
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_tasks'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/logout/')
def logout():
    if session.get('user'):
        session.clear()
    return redirect(url_for('login'))

@app.route('/tasks/new/', methods=['GET', 'POST'])
@requires_user_login
def new_task():
    # If submit button was pressed
    if request.method == 'POST': 
        # set fields of task equal to values fetched from HTML form
        title = request.form['title'].strip()
        text = request.form['taskText'].strip()

        from datetime import datetime
        today = datetime.now().strftime('%m-%d-%Y %I:%M %p')
        pinned = False
        # Task constructor raises exceptions if the fields aren't valid
        try:
            new_task = Task(title, text, today, pinned)
            new_task.author = session['user_id']
        except ValueError as err:
            # flash will display an error on screen, err.args[0] is the text from the exception
            flash(f'Invalid input: {err.args[0]}')
            # refreshes page
            return redirect(url_for('new_task'))
        
        db.session.add(new_task)
        db.session.commit()
    
        return redirect(url_for('get_tasks'))
    # if page was loaded normally via GET 
    else:
        return render_template('new.html', user=session['user'])


@app.route('/tasks/', methods=['GET', 'POST'])
@requires_user_login
def get_tasks():
    tasks = db.session.query(Task).all()
    sort_func = lambda task: task.id
    if session.get('order_by') is None or session.get('sort_ascending') is None:
        session['order_by'] = 'default'
        session['sort_ascending'] = True
    elif session['order_by'] == 'title':
        sort_func = lambda task: task.title.lower()
    elif session['order_by'] == 'date':
        sort_func = lambda task: task.date

    tasks.sort(key=sort_func, reverse=not session['sort_ascending'])
    tasks.sort(key=lambda task: not task.pinned)
    return render_template('tasks.html', tasks=tasks, user=session['user'])

@app.route('/tasks/order_by_<order>')
@requires_user_login
def set_task_order(order):
    # if the new sorting key is the same as the old one
    if session['order_by'] == order:
        # if sorting is descending and user hits button it should 
        # switch back to default sorting order
        if not session['sort_ascending']:
            session['order_by'] = 'default'
        # the direction of sorting should always toggle
        session['sort_ascending'] = not session['sort_ascending']
    # if the new sorting order is different from the old one
    else:
        session['sort_ascending'] = True
        session['order_by'] = order
    
    return redirect(url_for('get_tasks'))
        
@app.route('/tasks/<task_id>/')
@requires_user_login
def get_task(task_id):
    task = db.session.query(Task).filter_by(id=task_id).one()
    author = db.session.query(User).filter_by(id=task.author).one()
    form = CommentForm()
    comment_authors = {}
    for comment in task.comments:
        author = db.session.query(User).filter_by(id=comment.user_id).one()
        author_name = f'{author.first_name} {author.last_name}'
        comment_authors[comment] = author_name
    return render_template('task.html', task=task, user=session['user'], author=author, form=form, authors=comment_authors)
    
@app.route('/tasks/edit/<task_id>/', methods=['GET', 'POST'])
@requires_user_login
def update_task(task_id):
    if request.method == 'POST':
        title = request.form['title'].strip()
        text = request.form['taskText'].strip()
        task = db.session.query(Task).filter_by(id=task_id).one()
        try:
            task.title = title
            task.text = text
        except ValueError as err:
            # flash will display an error on screen, err.args[0] is the text from the exception
            flash(f'Invalid input: {err.args[0]}')
            # refreshes page
            return redirect(url_for('update_task', task_id=task_id))

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('get_tasks'))
    else:
        task = db.session.query(Task).filter_by(id=task_id).one()
        return render_template('new.html', task=task, user=session['user'])

@app.route('/tasks/delete/<task_id>/', methods=['POST'])
@requires_user_login
def delete_task(task_id):
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    db.session.delete(my_task)
    db.session.commit()
    return redirect(url_for("get_tasks"))

@app.route('/tasks/pin/<task_id>', methods=['POST'])
@requires_user_login
def pin_task(task_id):
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    my_task.pinned = not my_task.pinned
    db.session.add(my_task)
    db.session.commit()
    return redirect(url_for('get_tasks'))

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    if session.get('light_theme'):
        session['light_theme'] = not session['light_theme']
    else:
        session['light_theme'] = True
    return redirect(session['last'])

@app.route('/tasks/<task_id>/comment', methods=['POST'])
@requires_user_login
def new_comment(task_id):
    comment_form = CommentForm()
    # validate_on_submit only validates using POST
    if comment_form.validate_on_submit():
        # get comment data
        try:
            comment_text = request.form['comment'].strip()
            new_task = Comment(comment_text, int(task_id), session['user_id'])
        except ValueError as err:
        # flash will display an error on screen, err.args[0] is the text from the exception
            flash(f'Invalid input: {err.args[0]}')
            # refreshes page
            return redirect(url_for('get_task', task_id=task_id))
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for('get_task', task_id=task_id))

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

