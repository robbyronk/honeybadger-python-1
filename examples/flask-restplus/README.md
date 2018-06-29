# Flask example with Flask-Restplus

## Installation

Install the requirements in `requirements.txt`:

```bash
virtualenv env
. env/bin/activate

pip install -r requirements.txt
```

## Instructions

- Edit `app.py` and use your test project honeybadger API KEY.
- Run `FLASK_APP=app.py flask run --port 5000` to start the server.
- Visit [http://localhost:5000/fraction?a=1&b=2](http://localhost:5000/fraction?a=1&b=2) to see the app in action.
- Visit [http://localhost:5000/fraction?a=1&b=0](http://localhost:5000/fraction?a=1&b=0) to cause an exception. After a few seconds you should see the exception logged in [Honeybadger's UI](https://app.honeybadger.io). 