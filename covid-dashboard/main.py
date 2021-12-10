from flask import Flask
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

app = Flask(__name__)
with app.app_context():
    import widget_interface

if __name__ == "__main__":
    app.run()

