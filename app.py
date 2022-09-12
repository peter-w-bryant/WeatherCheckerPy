import requests 
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request, flash, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, validators, SelectField
from googletrans import Translator
from flask_mysqldb import MySQL
from datetime import datetime, tzinfo
from dateutil import tz
from pytz import timezone
import config

import os 

app = Flask(__name__)
app.secret_key = "not so secret key" # Generate a secret key.


#Config MySQL: HEROKU
app.config['MYSQL_HOST'] = config.host
app.config['MYSQL_USER'] = config.user
app.config['MYSQL_PASSWORD'] = config.password
app.config['MYSQL_DB'] = config.database
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Form for Login
class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    password = PasswordField('Password', [validators.Length(min=4, max=50)])

# Form for Registration
class RegisterForm(Form):
    new_username = StringField('Username', [validators.Length(max=50)])
    new_password = PasswordField('Password', [validators.Length(max=50)])
    confirm_password = PasswordField('Password', [validators.Length( max=50)])

# Form for MyCities
class MyCitiesForm(Form):
    new_location = StringField('City', [validators.Length(min=1, max=75)])

# Login PAGE
@app.route('/', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    session['logged_in'] = False
    session['user'] = False

    if request.method == 'POST': # If the form is submitted.
        username = form.username.data # Get the username from the form.
        password = form.password.data # Get the password from the form.
    
        # Create cursor
        cur = mysql.connection.cursor()

        # Search for the user in the database.
        result = cur.execute("SELECT * FROM users WHERE username = %s and password = %s", (username, password))

        # If the user is found in the database.
        if result > 0:
            session['logged_in'] = True # Set the session to True.
            session['user'] = username # Set the user in the session.
            flash("You have successfully logged in.", 'success') # Display a success message.
            return  redirect(url_for('search'))
        else:
          error = "Invalid username or password, please try again or continue as guest!"
          return render_template('login.html', error=error)
        
    return render_template('login.html')

    # Logout PAGE
@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear() # Clear the session.
    session['logged_in'] = False # Set the session to False.
    session['user'] = False # Set the user in the session to False.
    message = "You have successfully logged out."
    flash(message, 'success') # Display a success message.
    return redirect(url_for('login'))

# Registration PAGE
@app.route('/register', methods=['GET','POST'])
def Register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        new_username = form.new_username.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        # Create cursor
        cur = mysql.connection.cursor()
        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", (new_username,))
        if result > 0:
            error= "Username already taken, please try again!"
            return render_template('register.html', error= error)
        elif new_password != confirm_password:
            error = "Passwords do not match, please try again!"
            return render_template('register.html', error=error)
        # If newpassword length is less than 4 characters
        elif len(new_password) < 4:
            error = "Your password must be atleast 4 characters long, please try again!"
            return render_template('register.html', error=error)
        else:
            cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)", (new_username, new_password))
            mysql.connection.commit()
            msg = "Registration successful, please login!"
            return render_template('register.html', msg=msg)
    
    return render_template('register.html')

# Creates a route to the search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    city_state = None
    city_name = None
    user_cities = []
    if request.method == 'POST':
        new_city = request.form.get('city')            # Gets the location information from the form
        split_city = new_city.split(",")               # Delimits the location information by commas
        city_name = split_city[0]                      # Gets the city name
        session_location = (city_name, None)           # Creates a tuple for the session location, with no state
        if len(split_city) > 1:                        # If the length of the dilimited list is greater than 1, then there is a state
            city_state = split_city[1]                 # Gets the state if it exists
            session_location = (city_name, city_state) # Updates the tuple for the session location, with the state    
        if session_location != ('', None):
            user_cities.append(session_location)
            city_weather_data  = []                                # Create an empty list to store the weather data
            translator = Translator()                              # init the Google API translator
            geolocator = Nominatim(user_agent="geoapiExercises")   # initialize Nominatim API for geocoding
            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=e43ffd6c451ecd4a780de5ef3baa0519' # API call to get weather data
            
            for location in user_cities:
                city = location[0]                                 # Gets the city name from the session list
                if location[1] is not None:                        # If there is a state, then add it to the city name
                    location[1].strip()              # Removes any whitespace from the state
                state = location[1]                                # Gets the state name from the session list
                req = requests.get(url.format(city)).json() # # Uses the requests library to get the data for the current city from the OpenWeatherMap API

                # If the request returns a 404 error, flash a message, and delete the city from the database
                if req == {'cod': '404', 'message': 'city not found'}:
                    error = city +" is not a valid city!"
                    return render_template('weather.html', error=error)

                weather = {
                    'city': city,
                    'temperature': round(req['main']['temp']),       # Gets the temperature from the API
                    'feels_like': round(req['main']['feels_like']),  # Gets the feels like temperature from the API
                    'description': req['weather'][0]['description'].title(), # Gets the description from the API
                    'icon': req['weather'][0]['icon'],               # Gets the icon from the API

                    # Latitude and Longitude used to find the state of the city
                    'latitude': req['coord']['lat'],                 # Gets the latitude from the API
                    'longitude': req['coord']['lon'],                # Gets the longitude from the API

                    # Show more fields
                    'humidity': req['main']['humidity'],             # Gets the humidity from the API
                    'pressure': req['main']['pressure'],             # Gets the pressure from the API
                    'clouds': req['clouds']['all'],                  # Gets the cloudiness from the API
                    'wind_speed': req['wind']['speed'],              # Gets the wind speed from the API
                    'wind_deg': req['wind']['deg'],                  # Gets the wind direction from the API

                    # Find the sunrise and sunset times in the local timezone
                    
                    'sunrise': datetime.utcfromtimestamp(req['sys']['sunrise']).strftime('%I:%M %p'), # Gets the sunrise time from the API
                    'sunset': datetime.utcfromtimestamp(req['sys']['sunset']).strftime('%I:%M %p'),   # Gets the sunset time from the API

                }
                # Find the state corresponding to weather['latitude'] and weather['longitude']  
                lat = str(weather['latitude'])
                lon = str(weather['longitude'])
                location = geolocator.reverse(lat + ", " + lon)
                address = location.raw['address']
                # traverse the data
                country = address.get('country', '')

                if state == None:
                    weather['state'] = address.get('state', '')
                else:
                    weather['state'] =  state

                weather['country'] = country
                
                translation = translator.translate(country)

                weather['country_trans'] = translation.text


                city_weather_data.append(weather) # Appends the weather data for each city into the city_weather_data list

            # Render the template
            return render_template('weather.html', city_weather_data = city_weather_data)

    # Render the template
    return render_template('weather.html')

    # Creates a route to the search page
@app.route('/mycities', methods=['GET', 'POST'])
def mycities():
    city_name = ''
    city_state = ''
    # Access user id of the current user
    cur = mysql.connection.cursor()
    # Find user id of user by username
    cur.execute("SELECT user_id FROM users WHERE username = %s", [session.get('user')])
    user_id = cur.fetchone()
    # Convert user_id to int
    # print(user_id.get('user_id'))
    try:
        user_id = user_id.get('user_id')
    except:
        render_template('mycities.html')

    if request.method == 'POST' and  request.form.get('new_location') != None:
        new_location = request.form.get('new_location')
        split_city = new_location.split(",")               # Delimits the location information by commas
        city_name = split_city[0]                      # Gets the city name
        if len(split_city) > 1:                        # If the length of the dilimited list is greater than 1, then there is a state
            city_state = split_city[1]                 # Gets the state if it exists
        if city_name != '':
            # Insert city into city table with user_id
            cur.execute("INSERT INTO CITY(user_id, name, state) VALUES(%s, %s, %s)", (user_id, city_name, city_state))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()
            msg = city_name + ", " + city_state + " has been added to your cities!"
            return render_template('mycities.html', msg=msg)

    else:
        # For every entry in city table, if the city has the same user_id as the user, add it to the list of cities
        # Create cursor
        cur = mysql.connection.cursor()
        # Find all cities with the user_id
        cur.execute("SELECT * FROM CITY WHERE user_id = %s", [user_id])
        # Get the cities
        cities = cur.fetchall()
        # Close connection
        cur.close()

        city_weather_data  = []                                # Create an empty list to store the weather data
        translator = Translator()                              # init the Google API translator
        geolocator = Nominatim(user_agent="geoapiExercises")   # initialize Nominatim API for geocoding
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=e43ffd6c451ecd4a780de5ef3baa0519' # API call to get weather data

        # Iterate through the cities list
        for city in cities:
            city_name = city['name']                           # Gets the city name from the database
            city_state = city['state']                         # Gets the state name from the database
            req = requests.get(url.format(city_name)).json() # # Uses the requests library to get the data for the current city from the OpenWeatherMap API

            # If the request returns a 404 error, flash a message, and delete the city from the database
            if req == {'cod': '404', 'message': 'city not found'}:
                error = city_name + " is not a valid city!"
                return render_template('mycities.html', error=error)

            weather = {
                'city': city_name,
                'temperature': round(req['main']['temp']),       # Gets the temperature from the API
                'feels_like': round(req['main']['feels_like']),  # Gets the feels like temperature from the API
                'description': req['weather'][0]['description'].title(), # Gets the description from the API
                'icon': req['weather'][0]['icon'],               # Gets the icon from the API

                # Latitude and Longitude used to find the state of the city
                'latitude': req['coord']['lat'],                 # Gets the latitude from the API
                'longitude': req['coord']['lon'],                # Gets the longitude from the API

                # Show more fields
                'humidity': req['main']['humidity'],             # Gets the humidity from the API
                'pressure': req['main']['pressure'],             # Gets the pressure from the API
                'clouds': req['clouds']['all'],                  # Gets the cloudiness from the API
                'wind_speed': req['wind']['speed'],              # Gets the wind speed from the API
                'wind_deg': req['wind']['deg'],                  # Gets the wind direction from the API

                # Find the sunrise and sunset times  
                'sunrise': datetime.utcfromtimestamp(req['sys']['sunrise']).strftime('%I:%M %p'), # Gets the sunrise time from the API
                'sunset': datetime.utcfromtimestamp(req['sys']['sunset']).strftime('%I:%M %p'),   # Gets the sunset time from the API

                }
                # Find the state corresponding to weather['latitude'] and weather['longitude']  
            lat = str(weather['latitude'])
            lon = str(weather['longitude'])
            location = geolocator.reverse(lat + ", " + lon)
            address = location.raw['address']
            # traverse the data
            country = address.get('country', '')

            if city_state == '':
                weather['state'] = address.get('state', '')
            else:
                weather['state'] =  city_state

            weather['country'] = country
                
            translation = translator.translate(country)

            weather['country_trans'] = translation.text

            city_weather_data.append(weather) # Appends the weather data for each city into the city_weather_data list

            
        # Render the template
        return render_template('mycities.html', city_weather_data = city_weather_data)
    # Render the template
    return render_template('mycities.html')


if __name__ == '__main__':
    app.run(debug=True, port = 5000)
