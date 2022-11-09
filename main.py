import os                 # os is used to get environment variables IP & PORT
from flask import Flask, render_template, request, redirect, url_for
from database import db
from models import Task, User, user_tasks

app = Flask(__name__)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/index/')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks/new/', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['taskText']

        from datetime import date
        today = date.today().strftime('%m-%d-%Y')

        new_task = Task(title, text, today)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('get_tasks'))
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

        task.title = title
        task.text = text

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('get_tasks'))

    else:
        my_task = db.session.query(Task).filter_by(id=task_id).one()
        print(my_task.id)
        return render_template('new.html', task=my_task)

@app.route('/tasks/delete/<task_id>/', methods=['POST'])
def delete_task(task_id):
    my_task = db.session.query(Task).filter_by(id=task_id).one()
    db.session.delete(my_task)
    db.session.commit()
    return redirect(url_for("get_tasks"))

app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

