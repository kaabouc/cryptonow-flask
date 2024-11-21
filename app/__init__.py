import os
from flask import Flask
from flask_mongoengine import MongoEngine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Load configuration for MongoDB
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI')  # Make sure the Mongo URI is in the .env file

# Initialize the MongoDB connection using MongoEngine
db = MongoEngine(app)

# Import the models after initializing the db
from . import models

# Add your routes and other app logic here if necessary
@app.route('/')
def index():
    return 'Hello, Flask with MongoDB!'

# Optional: Run the app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)
