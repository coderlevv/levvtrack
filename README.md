# levvtrack

A basic Django-based web application for tracking daily food & nutrient intake.

This is a personal project developed for private use. The app works well
alongside a smartwatch or fitness tracker that records burned calories,
allowing intake and expenditure to be reviewed together.

## Installation

To install the app after cloning the repository and run it locally using the *development* server, follow the steps below.

**Do not use this setup for a production server.**


```bash
# Tested on a Ubuntu 24.04 LTS, python 3.12.3
cd levvtrack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open your browser and point it to the address given by the development server output (default http://127.0.0.1:8000).

## Basic Usage

Out of the box, the app supports tracking of total kcal intake.

On the **Entry** page click the *Add* button. Without any food items defined, you can enter a name for the entry and the total kcal value directly (which must be provided explicitly in this case).

### Adding nutrients
To enable more fine-grained tracking, you can define nutrients that should be tracked.

For example, to track fiber intake, go to the **Nutrient** page, press the *Add* button, enter the nutrient name (e.g. *Fiber*), and press *Save*.

### Adding food items
Once nutrients are defined, you can associate them with food items.

For example, to add broccoli to your item list, go to the **Item** page and click *Add*. Enter *Broccoli* as the item name and 30 as the item kcal value (per 100 g).

Open the nutrient menu, select *Fiber*, and enter the fiber content
(e.g. 2.9 g/100 g). Press *Add* to associate this nutrient with the item.

Repeat this process to add additional nutrients to food items.

### Adding Entries
After nutrients and items are available, they can be combined into entries representing consumed meals.

For example, if you had spaghetti with broccoli, click *Add* on the **Entry** page, name the entry accordingly, and add the consumed amounts of broccoli, spaghetti, and any other ingredients (which should be defined as items first).

After saving the entry, the **Entry** page is shown again, displaying the per day total consumed kcal and nutrients.

## Known issues
- The app currently operates in single-user mode. While multiple user
accounts can be created via the Django admin interface, records are not associated with individual users.

- Data export currently runs synchronously. With larger datasets, CSV
generation may take some time during which the browser tab remains blocked.

- Only grams (g) are supported as item and reference units by the UI at the moment. As a work around you can log in to Django admin (127.0.0.1:8000/admin) with your superuser credentials as created at installation and add additional units there.