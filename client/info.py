from telebot import TeleBot, types

from backend.models import BotUser, Channel, File, Vote, Information, Voting
from backend.templates import Messages, Keys, Smiles
from call_types import CallTypes
import utils, handlers


def bot_info_message(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    try:
        keyboard = handlers.menu_keyboard(user.lang)
        info = Messages.BOT_INFO.get(user.lang)
        bot.edit_message_text(text=info, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)
    except Exception as e:
        text = Messages.BOT_INFO_EXISTS.get(user.lang)
        bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)