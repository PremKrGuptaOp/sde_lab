/*
 * Formal Verification for Data Processor Module
 * 
 * This code models the core behavior of the DataProcessor module 
 * for formal verification using Frama-C.
 *
 * Author: Your Name
 * Date: May 11, 2025
 */

#include <stdlib.h>
#include <string.h>

// Define constants
#define MAX_USERS 100
#define MAX_PRODUCTS 200
#define MAX_INTERACTIONS 500
#define MAX_NAME_LENGTH 50
#define MAX_PATH_LENGTH 256

// Define interaction types
typedef enum {
    VIEW = 0,
    PURCHASE = 1,
    RATING = 2
} InteractionType;

// Data structures
typedef struct {
    char product_id[MAX_NAME_LENGTH];
    InteractionType type;
    char timestamp[26]; // ISO format timestamp
    float rating;
} Interaction;

typedef struct {
    char user_id[MAX_NAME_LENGTH];
    char name[MAX_NAME_LENGTH];
    int age;
    char **preferences; // Array of preference strings
    int preference_count;
    Interaction *interactions;
    int interaction_count;
} User;

typedef struct {
    char product_id[MAX_NAME_LENGTH];
    char name[MAX_NAME_LENGTH];
    char category[MAX_NAME_LENGTH];
    float price;
    float avg_rating;
    char description[256];
} Product;

typedef struct {
    char data_path[MAX_PATH_LENGTH];
    User users[MAX_USERS];
    int user_count;
    Product products[MAX_PRODUCTS];
    int product_count;
    char last_error[256];
    int data_loaded;
} DataProcessor;

// Function to initialize data processor
/*@ 
    requires \valid(processor);
    assigns processor->data_path[0 .. MAX_PATH_LENGTH-1], 
            processor->user_count, 
            processor->product_count, 
            processor->data_loaded, 
            processor->last_error[0];
    ensures processor->user_count == 0;
    ensures processor->product_count == 0;
    ensures processor->data_loaded == 0;
    ensures processor->last_error[0] == '\0';
*/
void initialize_data_processor(DataProcessor *processor) {
    processor->user_count = 0;
    processor->product_count = 0;
    processor->data_loaded = 0;
    processor->last_error[0] = '\0';
}

// Function to set data path
/*@ 
    requires \valid(processor);
    requires \valid_read(path);
    requires \valid(path + (0 .. MAX_PATH_LENGTH-1));
    assigns processor->data_path[0 .. MAX_PATH_LENGTH-1];
    ensures \forall int i; 0 <= i < strlen(path) ==> processor->data_path[i] == path[i];
*/
void set_data_path(DataProcessor *processor, const char *path) {
    strncpy(processor->data_path, path, MAX_PATH_LENGTH - 1);
    processor->data_path[MAX_PATH_LENGTH - 1] = '\0';
}

// Function to validate a product ID exists in the data processor
/*@ 
    requires \valid(processor);
    requires \valid_read(product_id);
    requires processor->data_loaded == 1;
    assigns \nothing;
    behavior product_exists:
        assumes \exists int i; 0 <= i < processor->product_count && 
                 strcmp(processor->products[i].product_id, product_id) == 0;
        ensures \result == 1;
    behavior product_not_exists:
        assumes \forall int i; 0 <= i < processor->product_count ==> 
                 strcmp(processor->products[i].product_id, product_id) != 0;
        ensures \result == 0;
    complete behaviors;
    disjoint behaviors;
*/
int product_exists(DataProcessor *processor, const char *product_id) {
    for (int i = 0; i < processor->product_count; i++) {
        if (strcmp(processor->products[i].product_id, product_id) == 0) {
            return 1;
        }
    }
    return 0;
}

// Function to validate all interactions reference valid products
/*@ 
    requires \valid(processor);
    requires processor->data_loaded == 1;
    requires processor->user_count > 0;
    requires processor->product_count > 0;
    assigns processor->last_error[0 .. 255];
    behavior all_valid:
        assumes \forall int i; 0 <= i < processor->user_count ==>
                 \forall int j; 0 <= j < processor->users[i].interaction_count ==>
                 (\exists int k; 0 <= k < processor->product_count &&
                  strcmp(processor->products[k].product_id, 
                         processor->users[i].interactions[j].product_id) == 0);
        ensures \result == 1;
        ensures processor->last_error[0] == '\0';
    behavior invalid_found:
        assumes \exists int i; 0 <= i < processor->user_count &&
                 \exists int j; 0 <= j < processor->users[i].interaction_count &&
                 (\forall int k; 0 <= k < processor->product_count ==>
                  strcmp(processor->products[k].product_id, 
                         processor->users[i].interactions[j].product_id) != 0);
        ensures \result == 0;
        ensures processor->last_error[0] != '\0';
    complete behaviors;
    disjoint behaviors;
*/
int validate_data_integrity(DataProcessor *processor) {
    for (int i = 0; i < processor->user_count; i++) {
        User *user = &processor->users[i];
        
        for (int j = 0; j < user->interaction_count; j++) {
            Interaction *interaction = &user->interactions[j];
            
            if (!product_exists(processor, interaction->product_id)) {
                snprintf(processor->last_error, 255, 
                         "Interaction references non-existent product: %s", 
                         interaction->product_id);
                return 0;
            }
        }
    }
    
    processor->last_error[0] = '\0';
    return 1;
}

// Function to add a product
/*@ 
    requires \valid(processor);
    requires \valid_read(product_id);
    requires \valid_read(name);
    requires \valid_read(category);
    requires processor->product_count < MAX_PRODUCTS;
    assigns processor->products[processor->product_count],
            processor->product_count;
    ensures processor->product_count == \old(processor->product_count) + 1;
    ensures strcmp(processor->products[\old(processor->product_count)].product_id, product_id) == 0;
*/
void add_product(DataProcessor *processor, const char *product_id, const char *name, 
                const char *category, float price, float avg_rating) {
    int idx = processor->product_count;
    
    strncpy(processor->products[idx].product_id, product_id, MAX_NAME_LENGTH - 1);
    processor->products[idx].product_id[MAX_NAME_LENGTH - 1] = '\0';
    
    strncpy(processor->products[idx].name, name, MAX_NAME_LENGTH - 1);
    processor->products[idx].name[MAX_NAME_LENGTH - 1] = '\0';
    
    strncpy(processor->products[idx].category, category, MAX_NAME_LENGTH - 1);
    processor->products[idx].category[MAX_NAME_LENGTH - 1] = '\0';
    
    processor->products[idx].price = price;
    processor->products[idx].avg_rating = avg_rating;
    
    processor->product_count++;
}

// Function to add a user
/*@ 
    requires \valid(processor);
    requires \valid_read(user_id);
    requires \valid_read(name);
    requires processor->user_count < MAX_USERS;
    assigns processor->users[processor->user_count],
            processor->user_count;
    ensures processor->user_count == \old(processor->user_count) + 1;
    ensures strcmp(processor->users[\old(processor->user_count)].user_id, user_id) == 0;
*/
void add_user(DataProcessor *processor, const char *user_id, const char *name, int age) {
    int idx = processor->user_count;
    
    strncpy(processor->users[idx].user_id, user_id, MAX_NAME_LENGTH - 1);
    processor->users[idx].user_id[MAX_NAME_LENGTH - 1] = '\0';
    
    strncpy(processor->users[idx].name, name, MAX_NAME_LENGTH - 1);
    processor->users[idx].name[MAX_NAME_LENGTH - 1] = '\0';
    
    processor->users[idx].age = age;
    processor->users[idx].interaction_count = 0;
    processor->users[idx].preference_count = 0;
    
    processor->user_count++;
}

// Function to add an interaction to a user
/*@ 
    requires \valid(processor);
    requires \valid_read(user_id);
    requires \valid_read(product_id);
    requires \valid_read(timestamp);
    requires 0 <= user_idx < processor->user_count;
    requires processor->users[user_idx].interaction_count < MAX_INTERACTIONS;
    assigns processor->users[user_idx].interactions[processor->users[user_idx].interaction_count],
            processor->users[user_idx].interaction_count;
    ensures processor->users[user_idx].interaction_count == \old(processor->users[user_idx].interaction_count) + 1;
*/
void add_interaction(DataProcessor *processor, int user_idx, const char *product_id, 
                    InteractionType type, const char *timestamp, float rating) {
    int idx = processor->users[user_idx].interaction_count;
    
    strncpy(processor->users[user_idx].interactions[idx].product_id, product_id, MAX_NAME_LENGTH - 1);
    processor->users[user_idx].interactions[idx].product_id[MAX_NAME_LENGTH - 1] = '\0';
    
    strncpy(processor->users[user_idx].interactions[idx].timestamp, timestamp, 25);
    processor->users[user_idx].interactions[idx].timestamp[25] = '\0';
    
    processor->users[user_idx].interactions[idx].type = type;
    processor->users[user_idx].interactions[idx].rating = rating;
    
    processor->users[user_idx].interaction_count++;
}

// Simulated test function
int main() {
    DataProcessor processor;
    
    // Initialize
    initialize_data_processor(&processor);
    
    // Set data path
    set_data_path(&processor, "data/sample_data.json");
    
    // Simulate data loading
    processor.data_loaded = 1;
    
    // Add products
    add_product(&processor, "prod1", "Wireless Headphones", "electronics", 129.99, 4.5);
    add_product(&processor, "prod2", "Fiction Bestseller", "books", 24.99, 4.2);
    
    // Add users
    add_user(&processor, "user1", "John Doe", 28);
    
    // Add interactions
    add_interaction(&processor, 0, "prod1", VIEW, "2025-04-01T10:30:15", 0.0);
    add_interaction(&processor, 0, "prod2", PURCHASE, "2025-04-01T11:20:30", 4.0);
    
    // Validate data integrity
    int valid = validate_data_integrity(&processor);
    
    return 0;
}