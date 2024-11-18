import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Step 1: Load the Excel file
def load_data(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path, engine='openpyxl')
    return df

# Step 2: Prepare the data for logistic regression
def prepare_data(df):
    # Assuming we want to predict if the price will go up (binary classification)
    df['price_increase'] = df['changePercent24Hr'].apply(lambda x: 1 if x > 0 else 0)
    features = ['priceUsd', 'marketCapUsd', 'volumeUsd24Hr', 'vwap24Hr']  # Select features
    X = df[features]
    y = df['price_increase']
    
    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y

# Step 3: Train the Logistic Regression model and save it as a .pkl file
def train_and_save_model(X, y, model_filename="logistic_regression_model.pkl"):
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Save the trained model as a .pkl file
    with open(model_filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved as {model_filename}")
    
    # Make predictions and evaluate the model
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

# Main function to execute the steps
if __name__ == "__main__":
    # Load data from Excel
    df = load_data("bitcoin_data_2024-11-18_10-30-45.xlsx")  # Replace with your file path
    
    # Prepare the data
    X, y = prepare_data(df)
    
    # Train the model and save it to a file
    train_and_save_model(X, y)
