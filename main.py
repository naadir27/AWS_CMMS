# Import the create_app function from the website module to initialize the Flask application
from website import create_app

# Initialize the Flask application using the create_app function
app = create_app()

# Run the application in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
