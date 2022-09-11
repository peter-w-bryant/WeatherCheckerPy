# WeatherCheckerPy: https://weather-checker-py.herokuapp.com/
A web-based database application that allows a user to create an account and search for current weather data for over 200,000 cities. Users who have signed in can add cities to their MyCities tab to quickly see current weather information for cities they are interested in. 

Alternatively, all users (including those who continue as guests from the login page) may search for one city at a time using the search interface. Current weather data is accessed from the OpenWeather API. Similarly, all city's states or territories are computed by passing the latitude and longitude coordinates of the city to Nominatim Geocoding API. All names are further translated to English using the Google Translate API.

The app is being hosted online and can be accessed here at: https://weather-checker-py.herokuapp.com/.

## User Login / Registration
https://user-images.githubusercontent.com/72423203/189508540-63560517-5b3f-406c-b3bb-4f9bdf95dd41.mp4

## Search Interface
https://user-images.githubusercontent.com/72423203/189508606-87043031-283d-42d7-8c3e-df22f4bc19f7.mp4

## My Cities Interface
https://user-images.githubusercontent.com/72423203/189508696-26f76bce-0bae-41c6-86eb-ffa6039a7c5c.mp4

## Running WeatherChecker.py Locally

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

