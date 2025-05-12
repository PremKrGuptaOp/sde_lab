"""
Data Processing Module for Product Recommendation Engine

This module is responsible for processing user interaction data and preparing it
for the recommendation algorithm. It handles data cleaning, feature extraction,
and preprocessing of user behavior data.

Author: Your Name
Date: May 11, 2025
"""

import json
import os
import numpy as np
from collections import defaultdict

class DataProcessor:
    def __init__(self, data_path=None):
        """
        Initialize the DataProcessor with optional data path.
        
        Args:
            data_path (str, optional): Path to the data file
        """
        self.data_path = data_path
        self.user_interactions = defaultdict(list)
        self.product_data = {}
        self.user_features = {}
        self.last_error = None
        
    def load_data(self, data_path=None):
        """
        Load data from JSON file.
        
        Args:
            data_path (str, optional): Path to override the instance data_path
            
        Returns:
            bool: True if data loading was successful, False otherwise
        """
        path = data_path or self.data_path
        
        if not path:
            self.last_error = "No data path provided"
            return False
            
        try:
            if not os.path.exists(path):
                self.last_error = f"Data file not found: {path}"
                return False
                
            with open(path, 'r') as file:
                data = json.load(file)
                
            # Validate data structure
            if not isinstance(data, dict):
                self.last_error = "Invalid data format: root must be a dictionary"
                return False
                
            if 'users' not in data or 'products' not in data:
                self.last_error = "Invalid data format: missing 'users' or 'products' keys"
                return False
                
            # Process and store data
            self._process_user_data(data['users'])
            self._process_product_data(data['products'])
            
            return True
            
        except json.JSONDecodeError:
            self.last_error = "Invalid JSON format in data file"
            return False
        except Exception as e:
            self.last_error = f"Error loading data: {str(e)}"
            return False
    
    def _process_user_data(self, users):
        """
        Process user data and extract interactions.
        
        Args:
            users (dict): Dictionary of user data
        """
        for user_id, user_data in users.items():
            if 'interactions' in user_data:
                self.user_interactions[user_id] = user_data['interactions']
            
            # Extract user features
            features = {k: v for k, v in user_data.items() if k != 'interactions'}
            self.user_features[user_id] = features
    
    def _process_product_data(self, products):
        """
        Process product data.
        
        Args:
            products (dict): Dictionary of product data
        """
        self.product_data = products
    
    def get_user_interaction_matrix(self):
        """
        Create a user-product interaction matrix.
        
        Returns:
            tuple: (matrix, user_indices, product_indices)
        """
        if not self.user_interactions or not self.product_data:
            return None, None, None
            
        # Create mappings for users and products
        user_ids = list(self.user_interactions.keys())
        product_ids = list(self.product_data.keys())
        
        user_idx = {uid: i for i, uid in enumerate(user_ids)}
        product_idx = {pid: i for i, pid in enumerate(product_ids)}
        
        # Create interaction matrix
        matrix = np.zeros((len(user_ids), len(product_ids)))
        
        for user_id, interactions in self.user_interactions.items():
            for interaction in interactions:
                if 'product_id' in interaction and 'rating' in interaction:
                    product_id = interaction['product_id']
                    if product_id in product_idx:
                        u_idx = user_idx[user_id]
                        p_idx = product_idx[product_id]
                        matrix[u_idx, p_idx] = float(interaction['rating'])
        
        return matrix, user_ids, product_ids
        
    def get_user_product_features(self, user_id):
        """
        Get combined features for a user and all products.
        
        Args:
            user_id (str): User ID to get features for
            
        Returns:
            dict: Dictionary mapping product IDs to feature vectors
        """
        if user_id not in self.user_features:
            return {}
            
        user_feature_dict = self.user_features[user_id]
        features = {}
        
        for product_id, product_data in self.product_data.items():
            # Combine user features and product features
            feature_vector = []
            
            # Add categorical features (e.g., user preferences matching product categories)
            if 'preferences' in user_feature_dict and 'category' in product_data:
                match_score = 1.0 if product_data['category'] in user_feature_dict['preferences'] else 0.0
                feature_vector.append(match_score)
                
            # Add numerical features
            if 'price' in product_data:
                feature_vector.append(float(product_data['price']))
                
            if 'avg_rating' in product_data:
                feature_vector.append(float(product_data['avg_rating']))
                
            # Previous interaction strength for this product
            interaction_score = 0
            for interaction in self.user_interactions.get(user_id, []):
                if interaction.get('product_id') == product_id:
                    interaction_score = float(interaction.get('rating', 0))
                    break
            feature_vector.append(interaction_score)
                
            features[product_id] = feature_vector
            
        return features
    
    def validate_data_integrity(self):
        """
        Validate the integrity of the loaded data.
        
        Returns:
            bool: True if data passes integrity checks, False otherwise
        """
        # Check if data is loaded
        if not self.user_interactions or not self.product_data:
            self.last_error = "No data loaded or empty data"
            return False
            
        # Validate user interaction references to products
        for user_id, interactions in self.user_interactions.items():
            for i, interaction in enumerate(interactions):
                if 'product_id' not in interaction:
                    self.last_error = f"Missing product_id in interaction {i} for user {user_id}"
                    return False
                    
                product_id = interaction['product_id']
                if product_id not in self.product_data:
                    self.last_error = f"Interaction references non-existent product: {product_id}"
                    return False
        
        return True
    
    def get_error(self):
        """
        Get the last error message.
        
        Returns:
            str: Last error message or None if no error
        """
        return self.last_error