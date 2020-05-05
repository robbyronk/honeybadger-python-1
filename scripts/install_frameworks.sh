#!/bin/sh
set -ev

echo $DJANGO_VERSION
echo $FLASK_VERSION

[ ! -z "$DJANGO_VERSION" ] && pip install Django==$DJANGO_VERSION
[ ! -z "$FLASK_VERSION" ] && pip install Flask==$FLASK_VERSION
echo "OK"