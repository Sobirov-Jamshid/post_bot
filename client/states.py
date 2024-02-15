from telebot import TeleBot, types

from backend.models import BotUser, Channel
from backend.templates import Messages, Keys, Smiles
from call_types import CallTypes
import handlers, commands


def add_channel(bot: TeleBot, message):
    chat_id = message.from_user.id
    user = BotUser.objects.get(chat_id=chat_id)
    try:
        user.bot_state = None
        user.save()
        channel = Channel.objects.filter(chat_id=message.forward_from_chat.id)
        
        if channel.exists():
            text = Messages.EXISTS_CHANNEL.get(user.lang).format(user=channel.get().user)
            bot.send_message(chat_id=chat_id, text=text, reply_markup=handlers.back_keyboard(user))
        else:
            m = bot.get_chat_administrators(message.forward_from_chat.id)
            Channel.objects.create(
                user=user,
                title=message.forward_from_chat.title,
                chat_id=message.forward_from_chat.id
            )
            text = Messages.SUCCESFUL_ADDED.get(user.lang)
            bot.send_message(chat_id=chat_id, text=text, reply_markup=handlers.menu_keyboard(user.lang))
        
    except Exception as e:
        print(e)
        text = Messages.NOT_ADMIN.get(user.lang)
        bot.send_message(chat_id=chat_id, text=text, reply_markup=handlers.back_keyboard(user))