# cob: type=views mountpoint=/bundle/index
from cob import route

@route('/')
def index():
    return 'hey'
