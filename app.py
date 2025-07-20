from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from scraper import AirlineScraper
from data_processor import DataProcessor
import plotly.graph_objs as go
import plotly.utils

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize components
scraper = AirlineScraper()
processor = DataProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape-data', methods=['POST'])
def scrape_data():
    try:
        # Get form data
        origin = request.form.get('origin', 'SYD')
        destination = request.form.get('destination', 'MEL')
        date_range = request.form.get('date_range', '7')
        
        # Scrape data
        raw_data = scraper.scrape_flight_data(origin, destination, int(date_range))
        
        # Process data
        insights = processor.process_data(raw_data)
        
        # Generate visualizations
        charts = processor.generate_charts(insights)
        
        return jsonify({
            'status': 'success',
            'data': insights,
            'charts': charts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/results')
def results():
    # Load cached data if available
    data_file = 'data/airline_data.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        return render_template('results.html', data=data)
    else:
        return render_template('results.html', data=None)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)