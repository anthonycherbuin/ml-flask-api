import os
import json
from flask import Flask
from flask import request
from flask import Response
from datetime import datetime
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
url:Final = 'https://v1.hockey.api-sports.io/games'
url_odds:Final = 'https://v1.hockey.api-sports.io/odds'


async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Headers including the API key
    headers = {
        'x-apisports-key': API_SPORT
    }

    # Parameters for the request
    payload = {
        'season': 2024,  # Swiss National League ID
        'league': 51,
        "timezone": "UTC+2",
    }

    # Make the request to the API with no proxy
    response = requests.request("GET",url, headers=headers, params=payload)

    matches = response.json()

    ns_matches = []
    for match in matches['response']:
        if match['status']['short'] == 'NS':
            ns_matches.append(match)
    
    if ns_matches:
        # Get the earliest match time
        earliest_match_time = min(ns_matches, key=lambda x: x['timestamp'])['timestamp']

        # Get all matches that happen at the earliest match time
        earliest_matches = [match for match in ns_matches if match['timestamp'] == earliest_match_time]

        for match in earliest_matches:
            # Extract relevant match information
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            match_date = match['date']

            # Convert the match date to a readable format
            date_object = datetime.fromisoformat(match_date)
            formatted_date = date_object.strftime("%d %B %Y at %HH%M")

            # # Parameters for the request
            # payload_odds = {
            #     'bet': 1, #1 is the id of the bet called '3Way Result' Home/draw/Away
            #     "game": match['id']
            # }

            # response_odds = requests.request("GET",url_odds, headers=headers, params=payload_odds)
            # odds = response_odds.json()

            match_info = (f"Next Swiss National League match:\n"
                        f"Home Team: {home_team}\n"
                        f"Away Team: {away_team}\n"
                        f"Date: {formatted_date}\n"
                        )
            # f"{home_team} have 52.3% chance to win this game. 🏆 \n"
            
            await update.message.reply_text(match_info)
            # await update.message.reply_text(odds['response'])
    else:
        await update.message.reply_text("No upcoming matches found for now.")

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
    await update.message.reply_text(f"An issue is happening on the API: {context.error}")
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