import os
from multiprocessing import Process
from flask import Flask
from dotenv import load_dotenv
import sys

# load environment variables
load_dotenv()
PORT = os.getenv('PORT', 4000)

# import files from different directory
sys.path.append('./src/InstaBot')
from InstagramBot import start_instabot

sys.path.append('./src/InstaLoader')
from content_retrieval import start_content

app = Flask(__name__)


# index
# Flask Route, try 'http://localhost:3000/' when running
@app.route('/')
def index():
    return "Instagram Bot Running"


def start_flask_application():
    print("Starting Flask app...")
    app.run(port=PORT)


def start_content_retrieval():
    start_content()


if __name__ == "__main__":

    flask_process = Process(target=start_flask_application)
    flask_process.start()

    # Setup Content Retrieval
    retrieval_process = Process(target=start_content_retrieval)
    retrieval_process.start()

    # Setup Content Posting
    start_instabot()
