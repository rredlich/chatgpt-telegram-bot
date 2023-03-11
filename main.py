from dotenv import load_dotenv
import os
import openai

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler

# Usesful links
# https://platform.openai.com/docs/guides/chat/introduction
# https://core.telegram.org/bots/features#creating-a-new-bot

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start states
STORE_SYS_PROMPT, TEST_USER_PROMPT = range(2)

# Global variables
gpt_sys_prompt = "You are a helpful assistant"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and ask for the system prompt."""
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text="👋\n¡Hola! Soy el bot de telegram conectado a la API de chatgpt.\n"
        "Envía /cancel para dejar de conversar conmigo.\n\n"
        "¿Cuál es el system prompt que quieres definir?",
    )

    return STORE_SYS_PROMPT
    
async def store_sys_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the system prompt and ask for the first message."""
    user = update.message.from_user
    chat_id = update.effective_chat.id

    global gpt_sys_prompt
    gpt_sys_prompt = update.message.text
    
    logger.info("%s: Language of %s: %s", chat_id, user.first_name, gpt_sys_prompt)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"El system prompt que voy a usar de ahora en adelante es\n{gpt_sys_prompt}\n\n"
            "Hagamos una prueba. Escribe un user prompt.",
    )

    return TEST_USER_PROMPT

async def test_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send the first user promopt to OpenAI API."""
    user = update.message.from_user
    chat_id = update.effective_chat.id

    gpt_user_prompt = update.message.text
    
    logger.info("%s: Language of %s: %s", chat_id, user.first_name, gpt_user_prompt)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{gpt_sys_prompt}"},
            {"role": "user", "content": f"{gpt_user_prompt}"}
        ]
    )
    
    await context.bot.send_message(chat_id=chat_id, text=completion.choices[0].message.content)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and finish the chat with the user."""
    chat_id = update.effective_chat.id

    user = update.message.from_user
    logger.info("%s: User %s canceled the conversation.", chat_id, user.first_name)
    await update.message.reply_text(
        "👋\n¡Adiós! Si quieres retomar la conversación, escribe /start.",
    )
    return ConversationHandler.END

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat with the user using OpenAI API."""
    gpt_user_prompt = update.message.text

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{gpt_sys_prompt}"},
            {"role": "user", "content": f"{gpt_user_prompt}"}
        ]
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=completion.choices[0].message.content)

async def show_sys_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the system prompt."""
    chat_id = update.effective_chat.id

    await context.bot.send_message(chat_id=chat_id, text=f"{gpt_sys_prompt}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Add conversation handler with the states STORE_SYS_PROMPT and TEST_USER_PROMPT
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STORE_SYS_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_sys_prompt)],
            TEST_USER_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_user_prompt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
    sys_prompt_handler = CommandHandler('vocab', show_sys_prompt)
    
    application.add_handler(conv_handler)
    application.add_handler(chat_handler)
    application.add_handler(sys_prompt_handler)
    
    application.run_polling()