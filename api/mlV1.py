from flask import Flask, request, jsonify


# Creating Flask instance
app = Flask(__name__)

# Creating an Endpoint to receive the data
# to make prediction on.
@app.route('/predict', methods=['POST'])
def predict():
    # Getting the data from the request
    home_team = request.form.get('home_team')
    away_teams = request.form.get('away_teams')
    
    # Return the Result
    return { 'away team: ' : away_teams, 'home_team': home_team}

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
