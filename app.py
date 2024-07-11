import pandas as pd

from flask import Flask, request, jsonify
from fastai.vision.all import *

app = Flask(__name__)

# Load the model
learn = load_learner('model_v1.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    pass
    Home = request.form.get('home_team')
    Away = request.form.get('away_team')
    OddsTeamA = float(request.form.get('OddsTeamA'))
    OddsX = float(request.form.get('OddsX'))
    OddsTeamB = float(request.form.get('OddsTeamB'))

    print("post incoming")

    new_data = pd.DataFrame({
        'Home': [Home],
        'Away': [Away],
        'OddsTeamA': [OddsTeamA],
        'OddsTeamB': [OddsTeamB],
        'OddsX': [OddsX]
    })

    dl = learn.dls.test_dl(new_data)
    preds, _ = learn.get_preds(dl=dl)
    prediction = preds[0].tolist()

    return jsonify({'prediction': prediction, 'away_team': Away, 'home_team': Home})



