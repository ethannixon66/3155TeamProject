from database import db
from sqlalchemy.orm import validates
class Task(db.Model):

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))

    def __init__(self, title, text, date):
        self.title = title
        self.text = text
        self.date = date

    @validates('title')
    def validate_title(self, key, value):
        if len(value) > Task.title.type.length:
            raise ValueError(f"Title cannot be longer than {Task.title.type.length} characters")
        elif len(value) < 1:
            raise ValueError(f"Title cannot be empty")
        elif db.session.query(Task).filter_by(title=value).first() is not None:
            raise ValueError(f"Task with that title already exists")
        return value

    @validates('text')
    def validate_text(self, key, value):
        if len(value) > Task.text.type.length:
            raise ValueError(f"Description cannot be longer than {Task.text.type.length} characters")
        return value


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

user_tasks = db.Table('UserTasks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)


    
