""" Runner file for the Flask Application"""
from media import app

if __name__ == "__main__":
    # Can change this to false, if not testing
    app.run(debug=True)
