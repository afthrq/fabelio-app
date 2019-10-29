# Fabelio Product Price Tracking

## What is this about
This project is a simple application made using Django to keep track of any information about any given Fabelio products.

## How this thing works
User will need to fill url to their desired Fabelio product to monitor their price. This application will store that informations into the database and will get any other important information (price, description, etc) using the product url as a reference with Scrapy as the scraping method.

## Architecture
There are 2 main components for this application to run:
1. Django app: this service will serve the frontend and the backend of the application.
2. Scrapy app: this service will crawl the given link and store it to the application database.


## How to use
### Manual
1. On this project root directory, run: `source fabeli/bin/activate`
   This will activate the virtual environment for the web app
2. After that install dependencies needed by running: `pip install -r requirements.txt`
   This will install all dependencies for this application written in `requirements.txt`
3. Modify the `settings.py` in the `DATABASE` section to match your running mysql settings
4. Run migration for the database by running: ` python migrate` 
5. After the dependencies installation succeded, run the web app by: `python manage.py runserver`
   This will bring the django application live on `localhost:8000`

### Docker
*Under development*

## Cavets
- The HTML scraping are being ran asynchronously, so when product is added, the ajax request will try 3 times until all the data needed are gathered. This could be a problem if the process of gathering data take longer.
