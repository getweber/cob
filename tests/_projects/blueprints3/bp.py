# cob: type=blueprint mountpoint=/
from flask import Blueprint

bp = Blueprint('bp', __name__)

@bp.route('bp1/test', defaults={'name': 'bp1'})
@bp.route('bp2/test', defaults={'name': 'bp2'})
def route(name):
    return 'this is {}'.format(name)
