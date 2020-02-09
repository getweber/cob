# cob: type=models
from cob import db

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
