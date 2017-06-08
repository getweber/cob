# cob: type=models
from cob import db

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
