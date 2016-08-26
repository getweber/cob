# cob: type=blueprint mountpoint=/
from flask import Blueprint

blueprint = Blueprint('bp', __name__)

@blueprint.route('/bp1/test', defaults={'name': 'bp1'})
@blueprint.route('/bp2/test', defaults={'name': 'bp2'})
def route(name):
    return 'this is {}'.format(name)
