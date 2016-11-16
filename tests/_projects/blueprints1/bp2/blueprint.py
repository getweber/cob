from flask import Blueprint

blueprint = Blueprint('bp2', __name__, url_prefix='/bp2')

@blueprint.route('/test')
def index():
    return 'this is bp2'
