import os
import json
from flask import Flask
from flask import request
from flask import Response
from datetime import datetime
from typing import Final
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)
TOKEN:Final = '7009352301:AAH3iq9mqT9mkSX-gweT4Q_ZS5wx6cpGPKk'
BOT_USERNAME:Final = "@LNA_prediction_bot"

# Your API key from API-Sports
API_SPORT:Final = '22024c3164521322f129b054c31798f4'

# Base URL for the API
url:Final = 'https://v1.hockey.api-sports.io/games'
url_odds:Final = 'https://v1.hockey.api-sports.io/odds'
url_MLV1:Final = 'http://localhost:3000/mlv1'


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


            # Parameters for the request
            payload_odds = {
                'bet': 1, #1 is the id of the bet called '3Way Result' Home/draw/Away
                "game": match['id']
            }

            # todo: finis integration of ML
            responseMl = requests.request("GET",url_MLV1, headers=headers, params=payload)
            # print('responseMl: ',responseMl.json())

            response_odds = requests.request("GET",url_odds, headers=headers, params=payload_odds)
            odds = response_odds.json()['response']
            response = ''

            if not odds:
                response = "⏳ oops, it's too early. Bookers have not opened the odds now. Try later."
            else:
                # Calculate the breakeven odds based on the ML prediction
                # Make the request to the API with no proxy
                responseMl = requests.request("GET",url_MLV1, headers=headers, params=payload)
                print('responseMl: ',responseMl)
                ml_probability = 0.60  # TODO: Replace this with the actual ML prediction
                oddsOkFrom = round(1 / ml_probability, 2)
                
                response = (
                    f"🏆 {home_team} have {ml_probability * 100:.1f}% chance to win this game.\n"
                    f"✅ It's worth betting on {home_team} if odds of the booker are higher than {oddsOkFrom}\n"
                )

            match_info = (
                f"Next Swiss National League match:\n"
                f"Home Team: {home_team}\n"
                f"Away Team: {away_team}\n"
                f"Date: {formatted_date}\n"
                f"\n"
                f"{response}"
            )

            await update.message.reply_text(match_info)
            # await update.message.reply_text(odds['response'])
    else:
        await update.message.reply_text("No upcoming matches found for now.")



def calculate_ev_per_unit(percentage_chance, odds):
    """
    This function calculates the expected value per unit based on the percentage chance and odds
    provided.
    
    :param percentage_chance: Percentage chance of an event occurring
    :param odds: The odds parameter represents the potential payout for a given outcome in a betting
    scenario. It is typically expressed as a ratio or a decimal. For example, if the odds are 2:1, it
    means that for every unit wagered, you would win 2 units if the outcome occurs
    """
    # Convert percentage chance to decimal
    probability_of_winning = percentage_chance / 100
    
    # Calculate the probability of losing
    probability_of_losing = 1 - probability_of_winning
    
    # Calculate EV per unit bet
    ev_per_unit = (probability_of_winning * odds) - probability_of_losing

    if ev_per_unit > 0:
        print(f"It's worth betting. Expected Value per unit bet: ${ev_per_unit:.2f}")
    else:
        print(f"It's not worth betting. Expected Value per unit bet: ${ev_per_unit:.2f}")
    
    return ev_per_unit

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