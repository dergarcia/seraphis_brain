# client_utils.py
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()           # reads OPENAI_API_KEY from your .env
client = OpenAI()       # single shared client for all scripts
