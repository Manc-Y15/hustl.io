# hustl.io
Y15 Group Project for 10120


# FOR TUTOR / MARKER

### Running the Server
- You must be in src/
- In order to run the server WITH DOCKER, use the "docker-compose build" command to build the docker images and "docker-compose up" to run the container.
- If docker doesn't work or you want to test without it, just go into src/ and run "python manage.py runserver"

### Layout
- src/
    - assets/ - All CSS, JS, IMG files
    - hustlio/ - The parent django app folder
        - settings.py is only significant file in here
    - main/ - The main django app folder, where all our important py files are
    - templates/ - The folder of all our HTML templates


### Points to note
- main/urls.py is where ALL our URL requests are redirected to view functions
- XXX_views.py are files containing view functions to handle requests and respond with a template + data
- This is the LOCAL version; it is running SQLite3 (no setup required) and has TEST data for prices, etc. This is why the historical data is irregular. If you would like to see data produced by the scheduler properly, go to hustlio.herokuapp.com/trading
- The price updates every 5 minutes, but the graphs change only at 00:00.


### Useful to Know
- In Django, model classes (models.py) represent SQL tables
- "<MODEL_NAME>.objects.all()" is equivalent to "SELECT * FROM <MODEL_NAME>"
- Django has a debug=True option to spit out errors when they occur. This is set to True on LOCAL but False on LIVE.


See LIVE version with LIVE data: hustlio.herokuapp.com/trading
