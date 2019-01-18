#!/bin/bash

cd shopify_challenge
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
