from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase
from models import DataEntry, db
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

db.connect()
db.create_tables([DataEntry], safe=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            
            # Insert data into database
            for _, row in df.iterrows():
                DataEntry.create(
                    name=row['name'],
                    age=row['age'],
                    country=row['country']
                )
            return redirect(url_for('visualization'))
    return render_template('upload.html')

DataEntry.create(name='Ibn Fadlan', age=78, country='Iran')
DataEntry.create(name='Ibn Battuta', age=66, country='Morocco')
DataEntry.create(name='Pork', age=5, country='Porkland')

@app.route('/visualization')
def visualization():
    data = DataEntry.select().dicts()
    df = pd.DataFrame(list(data))

    # Histogram example
    plt.figure(figsize=(10, 6))
    df['name'].hist(bins=20, color='blue')
    plt.title("Histogramma - name")
    plt.savefig('static/plots/histogram.png')
    plt.close()
    
    # Scatter plot example
    plt.figure(figsize=(10, 6))
    plt.scatter(df['name'], df['age'])
    plt.title("Scatter plot - name vs age")
    plt.savefig('static/plots/scatter.png')
    plt.close()

    return render_template('visualization.html')

if __name__ == '__main__':
    app.run(debug=True)