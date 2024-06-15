#!/usr/bin/sh
gunicorn -w 4 -b 0.0.0.0:5000 'tymheredd_gwe:app'
