import requests
import tkinter as tk
from tkinter import messagebox

API_KEY = '33b108f5a8a84cbd8da162728240708'
BASE_URL = 'http://api.weatherapi.com/v1/current.json'


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
    weather = get_weather(city)
    if 'error' in weather:
        messagebox.showerror("Error", weather['error'])
    else:
        result = f"City: {weather['city']}\nTemperature: {weather['temperature']}°C\nWeather: {weather['description']}\nHumidity: {weather['humidity']}%"
        result_label.config(text=result)


# Tkinter setup
root = tk.Tk()
root.title("Weather App")

tk.Label(root, text="Enter city name:").pack()
city_entry = tk.Entry(root)
city_entry.pack()
tk.Button(root, text="Get Weather", command=show_weather).pack()
result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
