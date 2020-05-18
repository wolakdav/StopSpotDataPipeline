from flask import Flask, render_template
import sys
import os
app = Flask(__name__)

@app.route('/')
def hello_world():
        return render_template('index.html')

@app.route('/shutdown')
def shutdown_ui():
        print('Shutting down StopSpot UI...')
        os._exit(2)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
