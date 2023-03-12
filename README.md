# 🤖 Chatgpt Telegram bot
Python script that connects a Telegram bot with OpenAI gpt-3.5 and whisper API. You can set the system prompt using the /start command and then send a user prompt writing a message. Also, you can send voice messages to transcript it.

# Requirements
* Python 3.7.1
* openai 0.27.0
* python-telegram-bot 20.1
* python-dotenv 0.21.1
* pydub 0.25.1
* ffprobe 0.5

# Setup
## Set your env file
1. Copy the .env-template file and renamed it .env

## Get your OpenAI API key
1. Create an account on OpenAI
2. On the side menu go to USER > API Keys (https://platform.openai.com/account/api-keys)
3. Click on Create a new secret key
4. Copy your secret API key and set it as the OPENAI_API_KEY in the .env file

## Create your Telegram bot and get your Telegram API key
1. Find BotFather in telegram and write the command /newbot
2. Set the name of your bot
3. Set the username of your bot (it must end with _bot)
5. Copy your bot secret API key and set it as the TELEGRAM_TOKEN in the .env file

## Start the Python script
```sh
python3 main.py
```

# How to use
1. Find your bot and send the command /start to set the system prompt. This prompt set the context for the chatbot. By default, the system prompt is "You are a helpful assistant"
2. Write a message to send a user prompt with the system prompt as context
3. You can also send a voice message to get a transcription