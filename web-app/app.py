from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    message = 'Hello, my sweet King!'
    return 'Hello, my sweet Queen!'+ ' ' + message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)