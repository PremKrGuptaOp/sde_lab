"""
Application Server for Product Recommendation Engine

This module serves as the main entry point for the Flask web application.
It handles routing, API endpoints, and integrates the recommendation system.

Author: Your Name
Date: May 11, 2025
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from datetime import datetime

# Import custom modules
from data_processor import DataProcessor
from recommendation import RecommendationEngine
from user_tracker import UserTracker

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Initialize data processor and recommendation engine
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_data.json')
data_processor = DataProcessor(DATA_PATH)
data_processor.load_data()
recommendation_engine = RecommendationEngine(data_processor)
recommendation_engine.train_collaborative_filter()

# Initialize user tracker
user_tracker = UserTracker(DATA_PATH)
user_tracker.load_interactions()

@app.route('/')
def index():
    """Render the home page with user selection and product catalog."""
    # Load data if not already loaded
    if not data_processor.product_data:
        data_processor.load_data()
    
    # Get users and products
    users = list(data_processor.user_features.keys())
    
    # Format products for display
    products = []
    for product_id, product in data_processor.product_data.items():
        product_copy = product.copy()
        product_copy['id'] = product_id
        products.append(product_copy)
    
    return render_template('index.html', users=users, products=products)

@app.route('/recommendations')
def recommendations():
    """Render recommendations for a specific user."""
    user_id = request.args.get('user_id')
    
    if not user_id or user_id not in data_processor.user_features:
        return redirect(url_for('index'))
    
    # Get user name
    user_name = data_processor.user_features[user_id].get('name', user_id)
    
    # Get recommendations
    recommendation_engine.train_collaborative_filter()
    
    # Use hybrid recommendations
    recommended_product_ids = recommendation_engine.get_hybrid_recommendations(user_id, top_n=6)
    
    # Format recommended products for display
    recommended_products = []
    for product_id in recommended_product_ids:
        if product_id in data_processor.product_data:
            product = data_processor.product_data[product_id].copy()
            product['id'] = product_id
            recommended_products.append(product)
    
    return render_template(
        'recommendations.html',
        user_id=user_id,
        user_name=user_name,
        products=recommended_products
    )

@app.route('/api/track_interaction', methods=['POST'])
def track_interaction():
    """API endpoint to track user interactions."""
    data = request.json
    
    if not data or 'user_id' not in data or 'product_id' not in data or 'type' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    user_id = data['user_id']
    product_id = data['product_id']
    interaction_type = data['type']
    value = data.get('value')
    
    # Track the interaction
    success = user_tracker.track_interaction(user_id, product_id, interaction_type, value)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to track interaction'})

@app.route('/api/user_interactions/<user_id>')
def get_user_interactions(user_id):
    """API endpoint to get user interactions."""
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user ID'})
    
    # Get recent interactions
    interactions = user_tracker.get_user_interactions(user_id, limit=10)
    
    # Enhance with product names
    for interaction in interactions:
        product_id = interaction.get('product_id')
        if product_id in data_processor.product_data:
            interaction['product_name'] = data_processor.product_data[product_id].get('name')
    
    return jsonify({'success': True, 'interactions': interactions})

# Development server configuration
if __name__ == '__main__':
    app.run(debug=True, port=5000)