# cob: type=views mountpoint=/test
from cob import route
from flask import render_template

@route('/')
def index():
    return render_template('index.html')
