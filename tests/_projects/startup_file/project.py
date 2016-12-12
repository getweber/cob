import gossip
import flask


@gossip.register('cob.after_configure_app')
def after_configure_app(app):

    @app.before_request
    def befoer_request():
        flask.g.acknowledgement = 'ack'
