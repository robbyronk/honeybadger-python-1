from honeybadger.fake_connection import send_notice

from testfixtures import log_capture
import json

@log_capture()
def test_send_notice_logging(l):
    config = {'api_key': 'aaa'}
    payload = json.dumps({'test': 'payload'})

    send_notice(config, payload)

    l.check(
        ('honeybadger.fake_connection', 'INFO', 'Using a fake connection. Will not make a real call to Honeybadger API'),
        ('honeybadger.fake_connection', 'INFO', 'The config used is {} with paylod {}'.format(config, payload)))
