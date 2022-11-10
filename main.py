import os                 # os is used to get environment variables IP & PORT
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from models import Task, User, user_tasks
from sqlalchemy.exc import NoResultFound
from forms import RegisterForm, LoginForm, CommentForm
import bcrypt

app = Flask(__name__)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'This is a secret'
db.init_app(app)

with app.app_context():
    db.create_all()

# runs if 404 error occurs (user typed a wrong url)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page does not exist")

# runs if NoResultFound exception is raised (the url contained an invalid task id)
@app.errorhandler(NoResultFound)
def task_not_found(e):
    return render_template('error.html', message="Whoops, looks like that task does not exist")

@app.route('/index/')
@app.route('/')
def index():
    if session.get('user') is None:
        redirect(url_for('login'))
    return render_template('index.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
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
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_tasks'))
    else:
        return render_template('register.html', form=form)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
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
def new_task():
    if session.get('user') is None:
        return redirect(url_for('login'))
    # If submit button was pressed
    if request.method == 'POST': 
        # set fields of task equal to values fetched from HTML form
        title = request.form['title'].strip()
        text = request.form['taskText'].strip()

        from datetime import date
        today = date.today().strftime('%m-%d-%Y')
        pinned = False
        # Task constructor raises exceptions if the fields are too long
        try:
            new_task = Task(title, text, today, pinned)
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
        return render_template('new.html')

@app.route('/tasks/', methods=['GET', 'POST'])
def get_tasks():
    if session.get('user') is None:
        return redirect(url_for('login'))
    _tasks = db.session.query(Task).all()
    _tasks.sort(key=lambda task: not task.pinned)
    return render_template('tasks.html', tasks=_tasks)

        

@app.route('/tasks/<task_id>/')
def get_task(task_id):
    if session.get('user') is None:
        return redirect(url_for('login'))
    a_task = db.session.query(Task).filter_by(id=task_id).one()
    return render_template('task.html', task=a_task)

@app.route('/tasks/edit/<task_id>/', methods=['GET', 'POST'])
def update_task(task_id):
    if session.get('user') is None:
        return redirect(url_for('login'))
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
            return redirect(url_for('new_task'))

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('get_tasks'))
    else:
        my_task = db.session.query(Task).filter_by(id=task_id).one()
        return render_template('new.html', task=my_task)

@app.route('/tasks/delete/<task_id>/', methods=['POST'])
def delete_task(task_id):
    if session.get('user') is None:
        return redirect(url_for('login'))
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    db.session.delete(my_task)
    db.session.commit()
    return redirect(url_for("get_tasks"))

@app.route('/tasks/pin/<task_id>', methods=['POST'])
def pin_task(task_id):
    print(session.get('user'))
    if session.get('user') is None:
        return redirect(url_for('login'))
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    my_task.pinned = not my_task.pinned
    db.session.add(my_task)
    db.session.commit()
    return redirect(url_for('get_tasks'))

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

