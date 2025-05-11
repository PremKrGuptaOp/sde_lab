"""
Recommendation Module for Product Recommendation Engine

This module implements the recommendation algorithm based on processed data.
It uses collaborative filtering and content-based approaches to generate
personalized product recommendations for users.

Author: Your Name
Date: May 11, 2025
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, data_processor):
        """
        Initialize the recommendation engine.
        
        Args:
            data_processor: DataProcessor instance with loaded data
        """
        self.data_processor = data_processor
        self.similarity_matrix = None
        self.user_indices = None
        self.product_indices = None
        
    def train_collaborative_filter(self):
        """
        Train collaborative filtering model based on user-item interaction matrix.
        
        Returns:
            bool: True if training was successful
        """
        # Get user-item interaction matrix
        matrix, user_indices, product_indices = self.data_processor.get_user_interaction_matrix()
        
        if matrix is None:
            return False
            
        # Store indices for future reference
        self.user_indices = user_indices
        self.product_indices = product_indices
        
        # Calculate item-item similarity matrix
        # Add small epsilon to avoid division by zero
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        self.similarity_matrix = cosine_similarity(matrix_norm.T)
        
        return True
        
    def get_collaborative_recommendations(self, user_id, top_n=5):
        """
        Get collaborative filtering based recommendations for a user.
        
        Args:
            user_id (str): User ID to get recommendations for
            top_n (int): Number of recommendations to return
            
        Returns:
            list: List of recommended product IDs
        """
        if self.similarity_matrix is None:
            return []
            
        try:
            # Get user index
            user_idx = self.user_indices.index(user_id)
        except ValueError:
            return []  # User not found
            
        # Get user's interaction vector
        matrix, _, _ = self.data_processor.get_user_interaction_matrix()
        user_vector = matrix[user_idx]
        
        # Products the user has already interacted with
        interacted_indices = np.where(user_vector > 0)[0]
        
        # Calculate predicted ratings for all items
        predicted_ratings = np.zeros(len(self.product_indices))
        
        for item_idx in range(len(self.product_indices)):
            if item_idx in interacted_indices:
                continue  # Skip items the user has already interacted with
                
            item_similarities = self.similarity_matrix[item_idx, interacted_indices]
            user_ratings = user_vector[interacted_indices]
            
            # Weighted sum of ratings
            if len(item_similarities) > 0:
                predicted_ratings[item_idx] = np.sum(item_similarities * user_ratings) / (np.sum(np.abs(item_similarities)) + 1e-10)
        
        # Get top N recommendations
        recommended_indices = np.argsort(predicted_ratings)[::-1][:top_n]
        return [self.product_indices[idx] for idx in recommended_indices]
        
    def get_content_based_recommendations(self, user_id, top_n=5):
        """
        Get content-based recommendations for a user.
        
        Args:
            user_id (str): User ID to get recommendations for
            top_n (int): Number of recommendations to return
            
        Returns:
            list: List of recommended product IDs
        """
        # Get user-product feature vectors
        features = self.data_processor.get_user_product_features(user_id)
        
        if not features:
            return []
            
        # Calculate scores for each product
        product_scores = {}
        for product_id, feature_vector in features.items():
            if not feature_vector:  # Skip if no features
                continue
                
            # Simple scoring based on feature values
            # This can be expanded with more sophisticated models
            score = sum(feature_vector)
            product_scores[product_id] = score
            
        # Sort products by score and return top N
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_products = [p[0] for p in sorted_products[:top_n]]
        
        return recommended_products
        
    def get_hybrid_recommendations(self, user_id, top_n=5, collab_weight=0.7):
        """
        Get hybrid recommendations combining collaborative and content-based approaches.
        
        Args:
            user_id (str): User ID to get recommendations for
            top_n (int): Number of recommendations to return
            collab_weight (float): Weight for collaborative filtering (0-1)
            
        Returns:
            list: List of recommended product IDs
        """
        # Get recommendations from both approaches
        collab_recs = self.get_collaborative_recommendations(user_id, top_n=top_n)
        content_recs = self.get_content_based_recommendations(user_id, top_n=top_n)
        
        # Combine recommendations with weights
        product_scores = {}
        
        # Score collaborative recommendations
        for i, product_id in enumerate(collab_recs):
            score = (top_n - i) * collab_weight
            product_scores[product_id] = product_scores.get(product_id, 0) + score
            
        # Score content-based recommendations
        content_weight = 1.0 - collab_weight
        for i, product_id in enumerate(content_recs):
            score = (top_n - i) * content_weight
            product_scores[product_id] = product_scores.get(product_id, 0) + score
            
        # Sort and return top recommendations
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_products[:top_n]]