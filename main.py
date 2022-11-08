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

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks/new', methods=['GET', 'POST'])
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
@app.route('/tasks')
def get_tasks():
    # a_user = db.Query(User).filter_by(email='example@email.com').one()
    _tasks = db.session.query(Task).all()
    return render_template('tasks.html', tasks=_tasks)



app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

