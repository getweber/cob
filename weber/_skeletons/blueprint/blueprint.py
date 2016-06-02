from flask import Blueprint

blueprint = Blueprint('{{name}}', __name__, url_prefix='{{mountpoint}}')
