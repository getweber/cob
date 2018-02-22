# cob: type=views mountpoint=/
from cob import route
from flask import g

@route('/')
def index():
    return g.acknowledgement
