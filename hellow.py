from flask import Flask
app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

@app.route('/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username
