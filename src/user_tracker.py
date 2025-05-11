"""
User Tracker Module for Product Recommendation Engine

This module tracks user behavior and interactions with products.
It records user actions like product views, clicks, and purchases.

Author: Your Name
Date: May 11, 2025
"""

import json
import os
from datetime import datetime

class UserTracker:
    def __init__(self, data_path=None):
        """
        Initialize the UserTracker with optional data path.
        
        Args:
            data_path (str, optional): Path to save user interaction data
        """
        self.data_path = data_path
        self.user_interactions = {}
        
    def load_interactions(self, data_path=None):
        """
        Load existing user interactions from file.
        
        Args:
            data_path (str, optional): Path to override the instance data_path
            
        Returns:
            bool: True if loading was successful, False otherwise
        """
        path = data_path or self.data_path
        
        if not path or not os.path.exists(path):
            return False
            
        try:
            with open(path, 'r') as file:
                data = json.load(file)
                
            if 'users' in data:
                for user_id, user_data in data['users'].items():
                    if 'interactions' in user_data:
                        self.user_interactions[user_id] = user_data['interactions']
                        
            return True
            
        except Exception:
            return False
    
    def save_interactions(self, data_path=None):
        """
        Save user interactions to file.
        
        Args:
            data_path (str, optional): Path to override the instance data_path
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        path = data_path or self.data_path
        
        if not path:
            return False
            
        try:
            # Load existing data if file exists
            data = {}
            if os.path.exists(path):
                with open(path, 'r') as file:
                    data = json.load(file)
                    
            # Update or create users section
            if 'users' not in data:
                data['users'] = {}
                
            # Update user interactions
            for user_id, interactions in self.user_interactions.items():
                if user_id not in data['users']:
                    data['users'][user_id] = {}
                data['users'][user_id]['interactions'] = interactions
                
            # Save data
            with open(path, 'w') as file:
                json.dump(data, file, indent=2)
                
            return True
            
        except Exception:
            return False
    
    def track_interaction(self, user_id, product_id, interaction_type, value=None):
        """
        Track a user interaction with a product.
        
        Args:
            user_id (str): User ID
            product_id (str): Product ID
            interaction_type (str): Type of interaction (view, click, purchase, rating)
            value (float, optional): Value associated with the interaction
            
        Returns:
            bool: True if tracking was successful
        """
        if not user_id or not product_id:
            return False
            
        # Initialize user if not exists
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = []
            
        # Create interaction record
        interaction = {
            'product_id': product_id,
            'type': interaction_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add value if provided
        if value is not None:
            interaction['value'] = value
            
            # For ratings, keep as a separate attribute
            if interaction_type == 'rating':
                interaction['rating'] = float(value)
        
        # Add interaction to user's history
        self.user_interactions[user_id].append(interaction)
        
        # Auto-save if data path is set
        if self.data_path:
            self.save_interactions()
            
        return True
        
    def get_user_interactions(self, user_id, limit=None):
        """
        Get interactions for a specific user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of interactions to return
            
        Returns:
            list: List of interaction records for the user
        """
        if user_id not in self.user_interactions:
            return []
            
        interactions = self.user_interactions[user_id]
        
        # Sort by timestamp (newest first)
        sorted_interactions = sorted(
            interactions, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # Apply limit if provided
        if limit and isinstance(limit, int) and limit > 0:
            return sorted_interactions[:limit]
            
        return sorted_interactions
        
    def get_product_interactions(self, product_id):
        """
        Get all interactions for a specific product across all users.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            list: List of interaction records for the product
        """
        product_interactions = []
        
        for user_id, interactions in self.user_interactions.items():
            for interaction in interactions:
                if interaction.get('product_id') == product_id:
                    # Add user ID to interaction data
                    interaction_copy = interaction.copy()
                    interaction_copy['user_id'] = user_id
                    product_interactions.append(interaction_copy)
        
        return product_interactions