# cob: mountpoint=/config
from cob import route
from cob.project import get_project

from flask import jsonify, current_app


@route('/')
def get_config():
    return jsonify({
        'flask_config': {
            key: current_app.config[key] for key in
            ['SECRET_KEY',
             'SQLALCHEMY_TRACK_MODIFICATIONS']
        },
        'cob_config': get_project().config,
    })
