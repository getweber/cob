from flask import Blueprint

blueprint = Blueprint('bp1', __name__, url_prefix='/bp1')

@blueprint.route('/test')
def index():
    return 'this is bp1'
