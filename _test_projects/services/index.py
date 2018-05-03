# cob: mountpoint=/
from cob import route
from cob import services

@route('/test_redis')
def test_redis():
    services.redis.set('key', 'value')
    value = services.redis.get('key')
    assert value.decode('utf-8') == 'value', f'Got {value!r} instead!'
    return 'ok'
