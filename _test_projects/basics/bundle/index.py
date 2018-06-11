# cob: type=views mountpoint=/bundle/index
from cob import route
from cob.project import get_project

from flask import jsonify

@route('/')
def index():
    return 'hey'


@route('/config')
def render_config():
    return jsonify(get_project().config)
