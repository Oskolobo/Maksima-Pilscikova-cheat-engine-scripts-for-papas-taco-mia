from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase
from models import DataEntry, db
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
    data = DataEntry.select().dicts()
    df = pd.DataFrame(list(data))

    # Create a histogram plot
    plt.figure(figsize=(10, 6))
    plt.hist(df['age'], bins=10, edgecolor='black')
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Frequency")

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df['name'], df['age'])
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