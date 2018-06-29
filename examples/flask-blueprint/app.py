import logging

from flask import Flask

from honeybadger.contrib import FlaskHoneybadger
from blueprint import simple_page

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'honeybadger-example'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
FlaskHoneybadger(app, report_exceptions=True)

app.register_blueprint(simple_page)
