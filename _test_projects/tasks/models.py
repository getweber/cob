# cob: type=models
from cob import db


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean, default=False)
