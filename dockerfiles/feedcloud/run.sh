#!/bin/bash

python manage.py collectstatic --no-input && python manage.py migrate && gunicorn feedcloud.wsgi -b 0:8000
