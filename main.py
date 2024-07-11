import threading
import os
import json
from datetime import datetime
from typing import Final
import requests
import pandas as pd

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from flask import Flask, request, jsonify
from fastai.vision.all import *
from app import app



TOKEN:Final = '7009352301:AAH3iq9mqT9mkSX-gweT4Q_ZS5wx6cpGPKk'
BOT_USERNAME:Final = "@LNA_prediction_bot"

# Your API key from API-Sports
API_SPORT:Final = '22024c3164521322f129b054c31798f4'

# Base URL for the API
url:Final = 'https://v1.hockey.api-sports.io/games'
url_odds:Final = 'https://v1.hockey.api-sports.io/odds'
url_MLV1:Final = 'https://python-telegram-bot-9rxn.onrender.com:8080/predict'


async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
    headers = {
        'x-apisports-key': API_SPORT
    }

    payload = {
        'season': 2024,  # Swiss National League ID
        'league': 51,
        "timezone": "UTC+2",
    }

    response = requests.get(url, headers=headers, params=payload)
    matches = response.json()

    ns_matches = [match for match in matches['response'] if match['status']['short'] == 'NS']

    if ns_matches:
        earliest_match_time = min(ns_matches, key=lambda x: x['timestamp'])['timestamp']
        earliest_matches = [match for match in ns_matches if match['timestamp'] == earliest_match_time]

        for match in earliest_matches:
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            match_date = match['date']
            date_object = datetime.fromisoformat(match_date)
            formatted_date = date_object.strftime("%d %B %Y at %H:%M")

            payload_odds = {
                'bet': 1,  # 1 is the id of the bet called '3Way Result' Home/draw/Away
                "game": match['id']
            }

            payload_ML = {
                'home_team': home_team,
                "away_team": away_team
            }

            response_odds = requests.get(url_odds, headers=headers, params=payload_odds)
            odds = response_odds.json()['response']

            responseMl = requests.post(url_MLV1, data=payload_ML)
            mlAnswer = responseMl.json()

            if not odds:
                response = "⏳ oops, it's too early. Bookers have not opened the odds now. Try later."
            else:
                ml_probability = mlAnswer.get('prediction', [0.6])[0]  # Replace with actual ML prediction
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
    else:
        await update.message.reply_text("No upcoming matches found for now.")


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'
    pass
    return 'I do not understand what you wrote...'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
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
    pass
    await update.message.reply_text(f"An issue is happening on the API: {context.error}")
    print(f'Update {update} caused error {context.error}')


def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('next_match', next_match))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_error_handler(error)

    print('Polling...')
    application.run_polling(poll_interval=3)


print('Starting bot and Flask app...')
run_telegram_bot()