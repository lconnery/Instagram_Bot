import os
from multiprocessing import Process
from dotenv import load_dotenv
import sys

# load environment variables
load_dotenv()
PORT = os.getenv('PORT', 4000)

# import files from different directory
from src.InstaBot.InstagramBot import InstagramBot

sys.path.append('./src/InstaLoader')
from content_retrieval import start_content


def start_content_retrieval():
    start_content()


if __name__ == "__main__":

    # Setup Content Retrieval
    retrieval_process = Process(target=start_content_retrieval)
    retrieval_process.start()

    # Setup Content Posting
    instagramBot = InstagramBot()
