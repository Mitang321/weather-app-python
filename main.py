import requests
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

API_KEY = '33b108f5a8a84cbd8da162728240708'
CURRENT_WEATHER_URL = 'http://api.weatherapi.com/v1/current.json'
FORECAST_URL = 'http://api.weatherapi.com/v1/forecast.json'


def create_user_table():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


def create_weather_table():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather
                 (city TEXT, temperature REAL, description TEXT, humidity INTEGER, timestamp TEXT, username TEXT)''')
    conn.commit()
    conn.close()


def create_favorite_table():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (username TEXT, city TEXT)''')
    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, password))
    user = c.fetchone()
    conn.close()
    return user


def update_user(username, new_username, new_password):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("UPDATE users SET username=?, password=? WHERE username=?",
              (new_username, new_password, username))
    conn.commit()
    conn.close()


def get_weather(city):
    try:
        response = requests.get(CURRENT_WEATHER_URL, params={
                                'key': API_KEY, 'q': city})
        data = response.json()
        if 'current' in data:
            weather = {
                'city': data['location']['name'],
                'temperature': data['current']['temp_c'],
                'description': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'username': current_user
            }
            return weather
        else:
            return {'error': 'Weather data not available'}
    except Exception as e:
        return {'error': str(e)}


def get_forecast(city):
    try:
        response = requests.get(FORECAST_URL, params={
                                'key': API_KEY, 'q': city, 'days': 3})
        data = response.json()
        if 'forecast' in data:
            forecast = []
            for day in data['forecast']['forecastday']:
                forecast.append({
                    'date': day['date'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'condition': day['day']['condition']['text']
                })
            return forecast
        else:
            return {'error': 'Forecast data not available'}
    except Exception as e:
        return {'error': str(e)}


def save_weather_to_db(weather):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?)",
              (weather['city'], weather['temperature'], weather['description'], weather['humidity'], weather['timestamp'], weather['username']))
    conn.commit()
    conn.close()


def show_weather():
    city = city_entry.get()
    if not city:
        messagebox.showerror("Error", "Please enter a city name")
        return

    weather = get_weather(city)
    if 'error' in weather:
        messagebox.showerror("Error", weather['error'])
    else:
        save_weather_to_db(weather)
        result = f"City: {weather['city']}\nTemperature: {weather['temperature']}°C\nWeather: {weather['description']}\nHumidity: {weather['humidity']}%"
        result_label.config(text=result)
        update_history()
        show_forecast()


def show_forecast():
    city = city_entry.get()
    forecast = get_forecast(city)
    if 'error' in forecast:
        forecast_label.config(text=forecast['error'])
    else:
        forecast_result = "3-Day Forecast:\n"
        for day in forecast:
            forecast_result += f"{day['date']} - Max: {day['max_temp']}°C, Min: {day['min_temp']}°C, Condition: {day['condition']}\n"
        forecast_label.config(text=forecast_result)


def update_history():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT city, temperature, description, humidity, timestamp FROM weather WHERE username=?", (current_user,))
    rows = c.fetchall()
    history = "\n".join(
        [f"{row[4]} - {row[0]}: {row[1]}°C, {row[2]}, {row[3]}%" for row in rows])
    history_label.config(text=f"Search History:\n{history}")
    conn.close()


def save_favorite():
    city = city_entry.get()
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("INSERT INTO favorites VALUES (?, ?)", (current_user, city))
    conn.commit()
    conn.close()
    update_favorites()


def update_favorites():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT city FROM favorites WHERE username=?", (current_user,))
    rows = c.fetchall()
    favorites = "\n".join([row[0] for row in rows])
    favorites_label.config(text=f"Favorites:\n{favorites}")
    conn.close()


def login():
    username = username_entry.get()
    password = password_entry.get()
    if authenticate_user(username, password):
        global current_user
        current_user = username
        login_frame.pack_forget()
        weather_frame.pack()
        update_history()
        update_favorites()
    else:
        messagebox.showerror("Error", "Invalid username or password")


def register():
    username = username_entry.get()
    password = password_entry.get()
    register_user(username, password)
    messagebox.showinfo("Success", "User registered successfully")


def update_profile():
    new_username = new_username_entry.get()
    new_password = new_password_entry.get()
    update_user(current_user, new_username, new_password)
    messagebox.showinfo("Success", "Profile updated successfully")
    current_user = new_username
    update_history()
    update_favorites()


# Tkinter setup
root = tk.Tk()
root.title("Weather App")

current_user = None

# Login Frame
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Username:").pack()
username_entry = tk.Entry(login_frame)
username_entry.pack()
tk.Label(login_frame, text="Password:").pack()
password_entry = tk.Entry(login_frame, show='*')
password_entry.pack()
tk.Button(login_frame, text="Login", command=login).pack()
tk.Button(login_frame, text="Register", command=register).pack()
login_frame.pack()

# Weather Frame
weather_frame = tk.Frame(root)
tk.Label(weather_frame, text="Enter city name:").pack()
city_entry = tk.Entry(weather_frame)
city_entry.pack()
tk.Button(weather_frame, text="Get Weather", command=show_weather).pack()
result_label = tk.Label(weather_frame, text="")
result_label.pack()
forecast_label = tk.Label(weather_frame, text="3-Day Forecast:")
forecast_label.pack()
history_label = tk.Label(weather_frame, text="Search History:")
history_label.pack()
favorites_label = tk.Label(weather_frame, text="Favorites:")
favorites_label.pack()
tk.Button(weather_frame, text="Save as Favorite", command=save_favorite).pack()

# Profile Update Frame
profile_frame = tk.Frame(root)
tk.Label(profile_frame, text="New Username:").pack()
new_username_entry = tk.Entry(profile_frame)
new_username_entry.pack()
tk.Label(profile_frame, text="New Password:").pack()
new_password_entry = tk.Entry(profile_frame, show='*')
new_password_entry.pack()
tk.Button(profile_frame, text="Update Profile", command=update_profile).pack()

create_user_table()
create_weather_table()
create_favorite_table()

root.mainloop()
