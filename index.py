import os.path
from master import config
from flask import Flask
from flask.ext.autoindex import AutoIndex

app = Flask(__name__)
AutoIndex(app, 'builds', add_url_rules=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.BUILDSLIST_PORT)
