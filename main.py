import requests
import sqlite3
import tkinter as tk
from tkinter import messagebox

API_KEY = '33b108f5a8a84cbd8da162728240708'
BASE_URL = 'http://api.weatherapi.com/v1/current.json'


def create_user_table():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
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


def get_weather(city):
    try:
        response = requests.get(BASE_URL, params={'key': API_KEY, 'q': city})
        data = response.json()
        if 'current' in data:
            weather = {
                'city': data['location']['name'],
                'temperature': data['current']['temp_c'],
                'description': data['current']['condition']['text'],
                'humidity': data['current']['humidity']
            }
            return weather
        else:
            return {'error': 'Weather data not available'}
    except Exception as e:
        return {'error': str(e)}


def show_weather():
    city = city_entry.get()
    if not city:
        messagebox.showerror("Error", "Please enter a city name")
        return

    weather = get_weather(city)
    if 'error' in weather:
        messagebox.showerror("Error", weather['error'])
    else:
        result = f"City: {weather['city']}\nTemperature: {weather['temperature']}°C\nWeather: {weather['description']}\nHumidity: {weather['humidity']}%"
        result_label.config(text=result)


def login():
    username = username_entry.get()
    password = password_entry.get()
    if authenticate_user(username, password):
        global current_user
        current_user = username
        login_frame.pack_forget()
        weather_frame.pack()
    else:
        messagebox.showerror("Error", "Invalid username or password")


def register():
    username = username_entry.get()
    password = password_entry.get()
    register_user(username, password)
    messagebox.showinfo("Success", "User registered successfully")


root = tk.Tk()
root.title("Weather App")

current_user = None

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

weather_frame = tk.Frame(root)
tk.Label(weather_frame, text="Enter city name:").pack()
city_entry = tk.Entry(weather_frame)
city_entry.pack()
tk.Button(weather_frame, text="Get Weather", command=show_weather).pack()
result_label = tk.Label(weather_frame, text="")
result_label.pack()

create_user_table()

root.mainloop()
