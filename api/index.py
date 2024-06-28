import os
import json
from flask import Flask
from flask import request
from flask import Response
from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)
TOKEN:Final = '7009352301:AAH3iq9mqT9mkSX-gweT4Q_ZS5wx6cpGPKk'
BOT_USERNAME:Final = "@LNA_prediction_bot"

# Your API key from API-Sports
API_SPORT:Final = '22024c3164521322f129b054c31798f4'

# Base URL for the API
url:Final = 'https://v1.hockey.api-sports.io/standings'


async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Headers including the API key
    headers = {
        'x-apisports-key': API_SPORT
    }

    # Parameters for the request
    payload = {
        'league': 15,  # Swiss National League ID
        'season': '2023-2024',  # Specify the season
    }

    # Make the request to the API with no proxy
    response = requests.request("GET",url, headers=headers, data=payload)

    # Parse the JSON response
    matches = response.json()
    print("debug:", response.text)

    # Check if there are any matches in the response
    if matches['response']:
        next_match = matches['response'][0]
        home_team = next_match['teams']['home']['name']
        away_team = next_match['teams']['away']['name']
        match_date = next_match['date']
        print(f"Next Swiss National League match: {home_team} vs {away_team} on {match_date}")
    else:
        await update.message.reply_text(f"An issue is happening on the API: {matches}")
    await update.message.reply_text(f"Next Swiss National League match: {home_team} vs {away_team} on {match_date}")


# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    return 'I do not understand what you wrote...'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"An issue is happening on the API{context.error}")
    print(f'Update {update} caused error {context.error}')


@app.route('/')
def index():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('help', next_match))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
    return Response("ok", status=200)