# levvtrack

A basic Django-based web application for food tracking.

## Installation

To install the app after cloning the repo and run it with a *development* server locally, follow the steps below. **Do *not* use this setup for a production server!**

```python
cd levvtrack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

