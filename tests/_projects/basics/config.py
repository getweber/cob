# cob: mountpoint=/config
from cob import route

from flask import jsonify, current_app


@route('/')
def get_config():
    return jsonify({
        key: current_app.config[key]
        for key in [
                'SECRET_KEY',
                'SQLALCHEMY_TRACK_MODIFICATIONS',
                ]
        })
