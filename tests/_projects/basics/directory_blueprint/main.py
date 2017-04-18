from flask import Blueprint

blueprint = Blueprint('directory_blueprint', __name__)

@blueprint.route('/test')
def index():
    return 'this is directory'
