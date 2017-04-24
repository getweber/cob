# cob: type=views mountpoint=/index
from cob import route

from . import mymodels

from flask import jsonify

@route('/list_models')
def get_all_models():
    return jsonify(mymodels.Person.query.all())
