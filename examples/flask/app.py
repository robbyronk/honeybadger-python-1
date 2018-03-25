import logging
from flask import Flask, request

from honeybadger.contrib import FlaskHoneybadger

logger = logging.getLogger(__name__)


def generic_div(a, b):
    """Simple function to divide two numbers"""
    logger.debug('Called generic_div({}, {})'.format(a, b))
    return a / b


app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'honeybadger-example'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
FlaskHoneybadger(app, report_exceptions=True)


@app.route('/')
def index():
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))

    logger.info('Dividing two numbers {} {}'.format(a, b))
    return str(generic_div(a, b))
