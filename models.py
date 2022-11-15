from database import db
from sqlalchemy.orm import validates
from datetime import date

# user_tasks = db.Table('UserTasks',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#     db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
# )

class Task(db.Model):

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    pinned = db.Column("pinned", db.Boolean())
    author = db.Column("author", db.Integer, db.ForeignKey('user.id'))
    # users = db.relationship('User', secondary=user_tasks, lazy='subquery', backref=db.backref('tasks', lazy=True))

    def __init__(self, title, text, date, pinned):
        self.title = title
        self.text = text
        self.date = date
        self.pinned = pinned

    @validates('title')
    def validate_title(self, key, value):
        existing_entry = db.session.query(Task).filter_by(title=value).first()
        if existing_entry is not None and existing_entry.id != self.id:
            raise ValueError(f"Task with that title already exists")
        elif len(value) > Task.title.type.length:
            raise ValueError(f"Title cannot be longer than {Task.title.type.length} characters")
        elif len(value) < 1:
            raise ValueError(f"Title cannot be empty")
        return value

    @validates('text')
    def validate_text(self, key, value):
        if len(value) > Task.text.type.length:
            raise ValueError(f"Description cannot be longer than {Task.text.type.length} characters")
        return value


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    authored_tasks = db.relationship("Task", backref="task", lazy=True)
    # tasks = db.relationship("Task", backref="user", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = date.today()




    
