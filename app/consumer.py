import os

from dotenv import load_dotenv

load_dotenv()

CONSUMER_USERNAME = os.getenv('CONSUMER_USERNAME', 'consumer')
CONSUMER_PASSWORD = os.getenv('CONSUMER_PASSWORD', '')