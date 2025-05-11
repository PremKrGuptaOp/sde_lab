"""
Test suite for the DataProcessor module.

This module tests the functionality of the DataProcessor class to ensure it
correctly loads, processes, and validates data for the recommendation engine.

Author: Your Name
Date: May 11, 2025
"""

import os
import sys
import json
import unittest
import tempfile
import numpy as np

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_path)

from data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a temporary sample data file
        self.temp_data_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        
        # Sample data for testing
        self.sample_data = {
            "users": {
                "user1": {
                    "name": "Test User",
                    "preferences": ["electronics", "books"],
                    "interactions": [
                        {"product_id": "prod1", "type": "view", "rating": 0},
                        {"product_id": "prod2", "type": "purchase", "rating": 4}
                    ]
                },
                "user2": {
                    "name": "Another User",
                    "preferences": ["fashion"],
                    "interactions": [
                        {"product_id": "prod3", "type": "purchase", "rating": 5}
                    ]
                }
            },
            "products": {
                "prod1": {
                    "name": "Test Product 1",
                    "category": "electronics",
                    "price": 99.99,
                    "avg_rating": 4.5
                },
                "prod2": {
                    "name": "Test Product 2",
                    "category": "books",
                    "price": 19.99,
                    "avg_rating": 4.0
                },
                "prod3": {
                    "name": "Test Product 3",
                    "category": "fashion",
                    "price": 49.99,
                    "avg_rating": 4.8
                }
            }
        }
        
        # Write sample data to the temporary file
        with open(self.temp_data_file.name, 'w') as f:
            json.dump(self.sample_data, f)
        
        # Create DataProcessor instance with the temporary file
        self.data_processor = DataProcessor(self.temp_data_file.name)
    
    def tearDown(self):
        """Clean up after each test."""
        # Delete the temporary file
        if os.path.exists(self.temp_data_file.name):
            os.unlink(self.temp_data_file.name)
    
    def test_load_data_success(self):
        """Test loading data successfully."""
        # Act
        result = self.data_processor.load_data()
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.data_processor.user_interactions), 2)
        self.assertEqual(len(self.data_processor.product_data), 3)
        self.assertIn("user1", self.data_processor.user_features)
        self.assertIn("prod1", self.data_processor.product_data)
    
    def test_load_data_file_not_found(self):
        """Test loading data with a non-existent file."""
        # Arrange
        processor = DataProcessor("non_existent_file.json")
        
        # Act
        result = processor.load_data()
        
        # Assert
        self.assertFalse(result)
        self.assertIn("not found", processor.last_error)
    
    def test_load_data_invalid_json(self):
        """Test loading data with invalid JSON."""
        # Arrange
        with open(self.temp_data_file.name, 'w') as f:
            f.write("This is not valid JSON")
        
        # Act
        result = self.data_processor.load_data()
        
        # Assert
        self.assertFalse(result)
        self.assertIn("Invalid JSON", self.data_processor.last_error)
    
    def test_load_data_missing_keys(self):
        """Test loading data with missing required keys."""
        # Arrange
        with open(self.temp_data_file.name, 'w') as f:
            json.dump({"only_users": {}}, f)
        
        # Act
        result = self.data_processor.load_data()
        
        # Assert
        self.assertFalse(result)
        self.assertIn("missing", self.data_processor.last_error)
    
    def test_get_user_interaction_matrix(self):
        """Test creation of user-product interaction matrix."""
        # Arrange
        self.data_processor.load_data()
        
        # Act
        matrix, user_ids, product_ids = self.data_processor.get_user_interaction_matrix()
        
        # Assert
        self.assertIsNotNone(matrix)
        self.assertIsInstance(matrix, np.ndarray)
        self.assertEqual(matrix.shape, (2, 3))  # 2 users, 3 products
        self.assertEqual(len(user_ids), 2)
        self.assertEqual(len(product_ids), 3)
        
        # Check specific values in the matrix
        user1_idx = user_ids.index("user1")
        prod2_idx = product_ids.index("prod2")
        self.assertEqual(matrix[user1_idx, prod2_idx], 4.0)  # user1's rating for prod2
    
    def test_get_user_product_features(self):
        """Test getting combined features for a user and products."""
        # Arrange
        self.data_processor.load_data()
        
        # Act
        features = self.data_processor.get_user_product_features("user1")
        
        # Assert
        self.assertIsNotNone(features)
        self.assertEqual(len(features), 3)  # 3 products
        
        # Check if electronic products get preference match score of 1.0
        # The first element of the feature vector should be the match score
        prod1_features = features.get("prod1")
        self.assertIsNotNone(prod1_features)
        self.assertEqual(prod1_features[0], 1.0)  # preference match (electronics)
        
        # Verify interaction score (last element in the feature vector)
        self.assertEqual(prod1_features[-1], 0.0)  # Rating 0 for prod1
        self.assertEqual(features["prod2"][-1], 4.0)  # Rating 4 for prod2
    
    def test_validate_data_integrity(self):
        """Test data integrity validation."""
        # Arrange
        self.data_processor.load_data()
        
        # Act
        result = self.data_processor.validate_data_integrity()
        
        # Assert
        self.assertTrue(result)
    
    def test_validate_data_integrity_invalid_product_reference(self):
        """Test data integrity with invalid product reference."""
        # Arrange
        self.data_processor.load_data()
        
        # Modify user interactions to reference a non-existent product
        self.data_processor.user_interactions["user1"].append({"product_id": "non_existent_prod"})
        
        # Act
        result = self.data_processor.validate_data_integrity()
        
        # Assert
        self.assertFalse(result)
        self.assertIn("non-existent product", self.data_processor.last_error)

if __name__ == '__main__':
    unittest.main()