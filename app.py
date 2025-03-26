from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase
from models import DataEntry, db
import requests
from datetime import datetime
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.connect()
db.create_tables([DataEntry], safe=True)
DEFAULT_HEADERS = {
        'User-Agent': 'ChessDataViewer/1.0 (https://yourdomain.com; contact@email.com)'
    }
@app.route('/', methods=['GET', 'POST'])
def index():
    print("Rendering index.html")
    if request.method == 'POST':
        username = request.form['username']
        return redirect(url_for('main1', username=username))
    return render_template('index.html')

@app.route('/main1/<username>')
def main1(username):
    data = process_username(username)
    return render_template('main1.html', data=data)

def process_username(username):
    # This should redirect to the page that shows all the data of the username
    print(f"Processing username: {username}")
    base_url = f"https://api.chess.com/pub/player/{username}"
    response = requests.get(
        base_url,
        headers=DEFAULT_HEADERS,
        timeout=5
    )
    response.raise_for_status()
    j = response.json()
    print(j)
    last_online = j["last_online"]
    l_o_month = int(last_online / 2_629_743)
    l_o_month_word = str(l_o_month % 12 + 1)
    if len(l_o_month_word) == 1:
        l_o_month_word = "0" + l_o_month_word
    #config the date from unix seconds to human language +-
    j["display_last_online"]=datetime.utcfromtimestamp(j["last_online"]).strftime('%Y-%m-%d %H:%M:%S')
    j["display_joined"]=datetime.utcfromtimestamp(j["joined"]).strftime('%Y-%m-%d %H:%M:%S')
    base_url = f"https://api.chess.com/pub/player/{username}/games/{1970 + l_o_month // 12}/{l_o_month_word}"
    response = requests.get(
        base_url,
        headers=DEFAULT_HEADERS,
        timeout=5
    )
    response.raise_for_status()
    games = response.json()
    print(games)
    return {'profile': j, 'games': games}

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print("Rendering upload.html")
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)

            # Check if the required columns exist
            required_columns = ['name', 'age', 'country']
            if not all(column in df.columns for column in required_columns):
                return "Error: The CSV file must contain the following columns: name, age, country", 400

            # Insert data into database
            for _, row in df.iterrows():
                DataEntry.create(
                    name=row['name'],
                    age=row['age'],
                    country=row['country']
                )
            return redirect(url_for('visualization'))
    return render_template('upload.html')

@app.route('/visualization')
def visualization():
    print("Rendering visualization.html")
    data = DataEntry.select().dicts()
    df = pd.DataFrame(list(data))

    # Create a histogram plot with a custom color
    plt.figure(figsize=(10, 6))
    plt.hist(df['age'], bins=10, edgecolor='black', color='skyblue')
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Frequency")

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Create a scatter plot with a custom color
    plt.figure(figsize=(10, 6))
    plt.scatter(df['name'], df['age'], color='green')
    plt.title("Scatter Plot - Name vs Age")
    plt.xlabel("Name")
    plt.ylabel("Age")

    # Save the scatter plot to a BytesIO object
    img_scatter = BytesIO()
    plt.savefig(img_scatter, format='png')
    img_scatter.seek(0)
    scatter_url = base64.b64encode(img_scatter.getvalue()).decode('utf8')
    plt.close()

    # Pass the plot URLs to the template
    return render_template('visualization.html', plot_url=plot_url, scatter_url=scatter_url)

if __name__ == '__main__':
    app.run(debug=True)