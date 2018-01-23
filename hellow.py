from flask import Flask

app = Flask(__name__)


# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

@app.route('/')
@app.route('/<username>')
def show_user_profile(username=None):
    # show the user profile for that user
    return 'User %s' % username


if __name__ == '__main__':
    app.run(port=8090, debug=True)
