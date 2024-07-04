from flask import Flask, request, jsonify
from fastai import *
from fastai.basic_train import load_learner
from fastai.vision.all import *
import pandas as pd
#exported with pandas 2.0.3
#fastai               2.7.15
#Flask                2.2.5

app = Flask(__name__)


learn = load_learner('model_v1.pkl')


@app.route('/predict', methods=['POST'])
def predict():
    # Getting the data from the request
    Home = request.form.get('home_team')
    Away = request.form.get('away_team')  # Corrected from 'away_teams'
    OddsTeamA = float(request.form.get('OddsTeamA'))
    OddsX = float(request.form.get('OddsX'))
    OddsTeamB = float(request.form.get('OddsTeamB'))

    print("post incoming")

    # Convert the incoming data to a DataFrame
    new_data = pd.DataFrame({
        'Home': [Home],  # Wrapped in a list
        'Away': [Away],  # Wrapped in a list
        'OddsTeamA': [OddsTeamA],
        'OddsTeamB': [OddsTeamB],
        'OddsX': [OddsX]
    })

    dl = learn.dls.test_dl(new_data)
    # # Get predictions
    preds, _ = learn.get_preds(dl=dl)
    prediction = preds[0].tolist()  # Convert tensor to list for JSON serialization

    # Return predictions
    return jsonify({'prediction': prediction, 'away team: ': Away, 'home_team': Home})

if __name__ == '__main__':
    app.run()