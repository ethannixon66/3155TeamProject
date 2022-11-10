from database import db
from sqlalchemy.orm import validates
class Task(db.Model):

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    pinned = db.Column("pinned", db.Boolean())

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
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

user_tasks = db.Table('UserTasks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)


    
