import os                 # os is used to get environment variables IP & PORT
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db
from models import Task, User, user_tasks
from sqlalchemy.exc import NoResultFound
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
    return 'Page does not exist'

# runs if NoResultFound exception is raised (the url contained an invalid task id)
@app.errorhandler(NoResultFound)
def task_not_found(e):
    return "Whoops, looks like that task doesn't exist"

@app.route('/index/')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks/new/', methods=['GET', 'POST'])
def new_task():
    # If submit button was pressed
    if request.method == 'POST': 
        # set fields of task equal to values fetched from HTML form
        title = request.form['title']
        text = request.form['taskText']

        from datetime import date
        today = date.today().strftime('%m-%d-%Y')
        # Task constructor raises exceptions if the fields are too long
        try:
            new_task = Task(title, text, today)
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

@app.route('/tasks/')
def get_tasks():
    _tasks = db.session.query(Task).all()
    return render_template('tasks.html', tasks=_tasks)

@app.route('/tasks/<task_id>/')
def get_task(task_id):
    a_task = db.session.query(Task).filter_by(id=task_id).one()
    return render_template('task.html', task=a_task)

@app.route('/tasks/edit/<task_id>/', methods=['GET', 'POST'])
def update_task(task_id):
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['taskText']
        
        task = db.session.query(Task).filter_by(id=task_id).one()
        try:
            task.title = title
            task.text = text
        except:
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
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    db.session.delete(my_task)
    db.session.commit()
    return redirect(url_for("get_tasks"))

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

