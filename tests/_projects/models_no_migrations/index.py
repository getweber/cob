# cob: type=views mountpoint=/index
from cob import route

from . import mymodels

from flask import jsonify


@route('/purge', methods=['POST'])
def purge():
    mymodels.Person.query.delete()
    mymodels.db.session.commit()
    return 'ok'

@route('/list_models')
def get_all_models():
    return jsonify([{'id': p.id} for p in mymodels.Person.query.all()])

@route('/add_model', methods=['POST'])
def add_model():
    mymodels.db.session.add(
        mymodels.Person())
    mymodels.db.session.commit()
    return 'ok'
