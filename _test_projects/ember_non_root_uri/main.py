# cob: type=views mountpoint=/
from cob import route

@route('/')
def index():
    return 'root resource here'
