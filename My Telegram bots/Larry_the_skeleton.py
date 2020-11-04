#!/usr/bin/env python3
import logging
from html import escape
from bing_image_downloader import downloader

import pickledb
import random

from telegram import ParseMode, TelegramError
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram.ext.dispatcher import run_async

BOTNAME = "Skuldy_the_bot"
TOKEN = '1402640149:AAE7dDGNAfye8lc4FgaPY1MSVNUPYZ3jnTQ'

# New Help
help_text = (
    "Hello darling... "
    "You can control me with these commands: \n"
    "/new_msg1 || /new_msg2 || /new_msg3 - Only admins can use this \n"
    "/delete_msgs - Only admins can use this \n"
    "/projects - A list of all open projects \n"
    "/angela - A reminder to Angela that she has pending payments with the group\n"
    "/photo <TEXT> - A cool picture \n"
    "...\n"
    "Okey fine... I don't know what else I can add\n"
    "Bye...\n\n"
)

"""
Create database object
Database schema:
<chat_id>_1 -> welcome message 1
<chat_id>_2 -> welcome message 2
<chat_id>_3 -> welcome message 3
<chat_id>_adm -> user id of the user who invited the bot
<chat_id>_lck -> boolean if the bot is locked or unlocked
<chat_id>_quiet -> boolean if the bot is quieted
chats -> list of chat ids where the bot has received messages in.
"""
# Create database object
db = pickledb.load("bot_the_skeleton.db", True)

if not db.get("chats"):
    db.set("chats", [])

# Set up logging
root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@run_async
def send_async(context, *args, **kwargs):
    context.bot.send_message(*args, **kwargs, disable_notification=True)


# In theory returns a list of admins
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def check(update, context, override_lock=None):
    """
    Perform some checks on the update. If checks were successful, returns True,
    else sends an error message to the chat and returns False.
    """

    chat_id = update.message.chat_id
    chat_str = str(chat_id)

    if chat_id > 0:
        send_async(context, chat_id=chat_id, text="Please add me to a group first!", )

        return False

    if update.message.from_user.id in get_admin_ids(context.bot, chat_id):
        return True

    send_async(context, chat_id=chat_id, text="You need to be admin first!", )

    return False


# Welcome a user to the chat
def welcome(update, context, new_member):
    """ Welcomes a user to the chat """

    message = update.message
    chat_id = message.chat.id
    logger.info(
        "%s joined to chat %d (%s)",
        escape(new_member.first_name),
        chat_id,
        escape(message.chat.title),
    )
    """ First message """
    # Pull the custom message for this chat from the database
    text = db.get(str(chat_id) + "_1")

    # Replace placeholders and send message
    text = text.replace("$username", new_member.first_name)
    text = text.replace("$title", message.chat.title)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML,
                             disable_notification=True)

    """ Second message """
    # Pull the custom message for this chat from the database
    text = db.get(str(chat_id) + "_2")

    if text != "False":
        # Send message
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML,
                                 disable_notification=True)

    """ Third message """
    # Pull the custom message for this chat from the database
    text = db.get(str(chat_id) + "_3")

    if text != "False":
        # Send message
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML,
                                 disable_notification=True)


# Introduce the bot to a chat its been added to
def introduce(update, context):
    """
    Introduces the bot to a chat its been added to and saves the user id of the
    user who invited us.
    """

    chat_id = update.message.chat.id
    invited = update.message.from_user.id

    logger.info(
        "Invited by %s to chat %d (%s)", invited, chat_id, update.message.chat.title,
    )

    db.set(str(chat_id) + "_adm", invited)
    db.set(str(chat_id) + "_lck", True)


# Print help text
def help(update, context):
    """ Prints help text """

    chat_id = update.message.chat.id
    chat_str = str(chat_id)
    if (
            not db.get(chat_str + "_quiet")
            or db.get(chat_str + "_adm") == update.message.from_user.id
    ):
        send_async(
            context,
            chat_id=chat_id,
            text=help_text,
            disable_web_page_preview=True,
        )


# Set custom message 1
def set_welcome_n1(update, context):
    """ Sets custom welcome first message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Split message into words and remove mentions of the bot
    message = update.message.text.partition(" ")[2]

    # Only continue if there's a message
    if not message:
        send_async(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
                 "<code>/set_msg_1 Hello $username, welcome to "
                 "$title!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Put message into database
    db.set(str(chat_id) + "_1", message)

    send_async(context, chat_id=chat_id, text="Got it!")


# Set custom message 2
def set_welcome_n2(update, context):
    """ Sets custom welcome first message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Split message into words and remove mentions of the bot
    message = update.message.text.partition(" ")[2]

    # Only continue if there's a message
    if not message:
        send_async(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
                 "<code>/welcome Hello $username, welcome to "
                 "$title!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Put message into database
    db.set(str(chat_id) + "_2", message)

    send_async(context, chat_id=chat_id, text="Got it!")


# Set custom message 3
def set_welcome_n3(update, context):
    """ Sets custom welcome message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Split message into words and remove mentions of the bot
    message = update.message.text.partition(" ")[2]

    # Only continue if there's a message
    if not message:
        send_async(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
                 "<code>/welcome Hello $username, welcome to "
                 "$title!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Put message into database
    db.set(str(chat_id) + "_3", message)

    send_async(context, chat_id=chat_id, text="Got it!")


# Delete all messages
def delete_messages(update, context):
    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Delete message
    db.set(str(chat_id) + "_1", False)
    db.set(str(chat_id) + "_2", False)
    db.set(str(chat_id) + "_3", False)

    # We made it!!
    send_async(
        context,
        chat_id=chat_id,
        text="Done!!",
        parse_mode=ParseMode.HTML,
    )


# Show open projects
def projects(update, context):
    chat_id = update.message.chat.id

    text = db.get(str(chat_id) + "_2")

    if text == "False":
        text = "No hay proyectos definidos"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML,
                             disable_notification=True)


def empty_message(update, context):
    """
    Empty messages could be status messages, so we check them if there is a new
    group member, someone left the chat or if the bot has been added somewhere.
    """

    # Keep chatlist
    chats = db.get("chats")

    if update.message.chat.id not in chats:
        chats.append(update.message.chat.id)
        db.set("chats", chats)
        logger.info("I have been added to %d chats" % len(chats))

    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            # Bot was added to a group chat
            if new_member.username == BOTNAME:
                return introduce(update, context)
            # Another user joined the chat
            else:
                return welcome(update, context, new_member)


def error(update, context, **kwargs):
    """ Error handling """
    error = context.error

    try:
        if isinstance(error, TelegramError) and (
                error.message == "Unauthorized"
                or error.message == "Have no rights to send a message"
                or "PEER_ID_INVALID" in error.message
        ):
            chats = db.get("chats")
            chats.remove(update.message.chat_id)
            db.set("chats", chats)
            logger.info("Removed chat_id %s from chat list" % update.message.chat_id)
        else:
            logger.error("An error (%s) occurred: %s" % (type(error), error.message))
    except:
        pass


def angela(update, context):
    text = "Ángela paga la coca!! Primer aviso!!!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML,
                             disable_notification=True)


# Unknown commands
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def download_photos(update, query_string):
    downloader.download(query_string, limit=10, output_dir='Larry_images',
                        adult_filter_off=True, force_replace=True, timeout=60)


def photo(update, context):
    """ Por el momento envíamos una foto de las almacenadas en el disco, es decir,"""
    """ primero descargamos X cantidad de fotos, y luego envíamos una al azar."""
    """ Pero, en vez de descargar las fotos, quiero almacenar en un array, las URL
        de los archivos descargables, y envíar uno al azar"""
    query_string = update.message.text.partition(" ")[2]
    download_photos(update, query_string)

    name = "Larry_images/" + query_string + "/Image_" + str(random.randrange(1, 10)) + ".jpg"

    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(name, "rb"))


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, workers=10, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("new_msg1", set_welcome_n1))
    dp.add_handler(CommandHandler("new_msg2", set_welcome_n2))
    dp.add_handler(CommandHandler("new_msg3", set_welcome_n3))
    dp.add_handler(CommandHandler("projects", projects))
    dp.add_handler(CommandHandler("angela", angela))
    dp.add_handler(CommandHandler("photo", photo))
    dp.add_handler(CommandHandler("delete_msgs", delete_messages))

    dp.add_handler(MessageHandler(Filters.status_update, empty_message))

    dp.add_error_handler(error)

    """Last handler"""
    unknown_handler = MessageHandler(Filters.command, unknown)
    dp.add_handler(unknown_handler)

    updater.start_polling(timeout=30, clean=True)
    updater.idle()


if __name__ == "__main__":
    main()
