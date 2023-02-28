"""
The purpose of this file is to forward Nginx requests to the flask app.
"""
from myproject import app

if __name__ == "__main__":
    app.run()
