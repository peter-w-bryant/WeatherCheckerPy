# WeatherCheckerPy: https://weather-checker-py.herokuapp.com/
A web-based database application that allows a user to create an account and search for current weather data for over 200,000 cities. Users who have signed in can add cities to their MyCities tab to quickly see current weather information for cities they are interested in. 

Alternatively, all users (including those who continue as guests from the login page) may search for one city at a time using the search interface. Current weather data is accessed from the OpenWeather API. Similarly, all city's states or territories are computed by passing the latitude and longitude coordinates of the city to Nominatim Geocoding API. All names are further translated to English using the Google Translate API.

The app is being hosted online and can be accessed here at: https://weather-checker-py.herokuapp.com/.


<h4>Running WeatherChecker.py Locally</h4>

<p>Clone my repository</p>

```python
$ git clone https://github.com/peter-w-bryant/WeatherCheckerPy.git
```
<p>Create + activate virtual environment</p>

```python
$ python -m venv ./env
$ env/Scripts/activate
```
<p>Install all dependencies</p>

```python
$ pip install -r requirements.txt
```

<p>Run the app and start your local server</p>

```python
$ python app.py
```

