
# !pip install pyTelegramBotAPI

import os
import telebot
import requests
# from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import json

BOT_TOKEN =
WEATHER_TOKEN =
OPENROUTER_API_KEY =

bot = telebot.TeleBot(BOT_TOKEN)

# List of supported commands
SUPPORTED_COMMANDS = ['/start', '/help', '/weather', '/list']

def validate_command(message):
  return (message.text.startswith('/')
    and message.text not in SUPPORTED_COMMANDS)

@bot.message_handler(func=validate_command)
def handle_unsupported_commands(message):
    bot.reply_to(message, "Sorry, that command is not supported. Type /list for a list of supported commands.")

@bot.message_handler(commands=['list'])
def list_command(message):
    '''
    Returns a welcome message when the '/list' command is sent by the user.
    '''
    bot.send_message(message.chat.id, f'Avaliable Commands:\n'+'\n'.join(SUPPORTED_COMMANDS))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    '''
    Returns a welcome message when the '/start' command is sent by the user.
    '''
    bot.send_message(message.chat.id, inject_personality('Greetings, fellow traveler! What weather secrets shall I uncover for you today?'))

@bot.message_handler(commands=['help'])
def send_welcome(message):
    '''
    Returns a welcome message when the '/help' command is sent by the user.
    '''
    bot.send_message(message.chat.id, inject_personality('How can I help you today.'))

@bot.message_handler(commands=['weather'])
def send_weather(message):
    '''
    Prompts the user to enter a location when the '/weather' command is sent.
    Registers the next step handler to wait for the user's input and calls the 'fetch_weather' function.
    '''
    location_prompt = '🔮 Where shall I conjure the weather forecast? (Enter a City or Town)'
    sent_message = bot.send_message(message.chat.id, inject_personality(location_prompt), parse_mode='Markdown')
    bot.register_next_step_handler(sent_message, fetch_weather)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    response = openrouter(message.text)
    bot.send_message(message.chat.id, response)

# Function to inject personality into responses
def inject_personality(response):
      # Add a dash of humor or quirkiness to the response
      return f"🌟 {response} 🌟"

def location_handler(message):
    '''
    Returns the latitude and longitude coordinates from the user's message (location) using the Nominatim geocoder.
    '''
    location = message.text
    geolocator = Nominatim(user_agent="my_app")

    try:
        location_data = geolocator.geocode(location)
        latitude = round(location_data.latitude, 2)
        longitude = round(location_data.longitude, 2)
        return latitude, longitude
    except AttributeError:
        return None, None

def get_weather(latitude, longitude):
    '''
    Constructs URL to make API call to OpenWeatherMap API and returns response JSON.
    '''
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={WEATHER_TOKEN}'
    response = requests.get(url)
    return response.json()

def fetch_weather(message):
    '''
    Called when the user provides a location in response to the '/weather' command.
    Fetches weather data and sends it to the user.
    '''
    latitude, longitude = location_handler(message)
    if latitude is None or longitude is None:
        bot.send_message(message.chat.id, inject_personality('⚠️ Alas! The weather spirits couldn\'t find that location. Please try another one.'))
        return

    weather = get_weather(latitude, longitude)
    if 'list' in weather:
        data = weather['list']
        current_weather = data[0]
        weather_description = current_weather['weather'][0]['description']
        main_info = current_weather['main']
        temperature_kelvin = main_info['temp']
        temperature_celsius = round(temperature_kelvin - 273.15, 1)
        humidity = main_info['humidity']
        wind_speed_mps = current_weather['wind']['speed']
        wind_speed_kph = round(wind_speed_mps * 3.6, 1)
        content = f'Talk about weather {weather_description} in funny and sarcastic way in maximum of 30 words.'
        creativity = f'Latest Facts About Weather in maximum of 30 words'
        generated_response = openrouter(content)
        generated_response_creativity = openrouter(creativity)


        weather_message = f'*Weather Forecast:* {weather_description}\n'
        weather_message += f'*Temperature:* {temperature_celsius}°C\n'
        weather_message += f'*Humidity:* {humidity}%\n'
        weather_message += f'*Wind Speed:* {wind_speed_kph} km/h\n'
        weather_message += f'{generated_response}\n'
        weather_message += f'*Facts About Weather:* {generated_response_creativity}\n'

        bot.send_message(message.chat.id, inject_personality('✨ Here\'s the mystical weather forecast! ✨'))
        bot.send_message(message.chat.id, weather_message, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, inject_personality('🧙‍♂️ Oops! The weather spell seems to have fizzled out. Try again later.'))

def openrouter(content):
  response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
      "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    },
    data=json.dumps({
      "model": "openai/gpt-3.5-turbo", # Optional
      "messages": [
        {"role": "user", "content": content}
      ]
    })
  )
  return response.json()['choices'][0]['message']['content']

bot.polling()