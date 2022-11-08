import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask is the web app that we will customize

app = Flask(__name__)     # create an app

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/')
def index():
    return 'Hello World!'


app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

