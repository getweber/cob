# cob: type=blueprint mountpoint=/blueprints/file
from flask import Blueprint

blueprint = Blueprint('file_blueprint', __name__)

@blueprint.route('/test')
def route():
    return 'this is file'
