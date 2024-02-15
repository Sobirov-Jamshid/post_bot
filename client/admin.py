from telebot import TeleBot, types
import time
import commands
from datetime import date
from backend.templates import Messages, Smiles, Keys
from backend.models import BotUser, Channel

def admin_commands_handler(bot: TeleBot, message):
    admin_list = [285151723, 1926669559]
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    keyboard.add(
        types.KeyboardButton(text=Keys.SEND_MESSAGE.get(user.lang)),
        types.KeyboardButton(text=Keys.STATISTICS.get(user.lang)),
        )
    keyboard.add(
        types.KeyboardButton(text=Keys.SEND_MESSAGE_CHANNEL.get(user.lang)),
    )
    keyboard.add(
        types.KeyboardButton(text=Keys.BACK.get(user.lang)),
    )
    if chat_id in admin_list:
        bot.send_message(chat_id=chat_id, text=Messages.ADMIN_PANEL_MESSAGE.get(user.lang), reply_markup=keyboard)

def statistics_commands_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    admin = BotUser.objects.get(chat_id=chat_id)
    user = BotUser.objects.all()
    bot.send_message(chat_id=chat_id, text=Messages.STATISTICS_MESSAGE.get(admin.lang).format(jami=user.count(), bugun=user.filter(created__gte=date.today()).count()))

def rassilka_commands_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 6
    user.save()
    bot.send_message(chat_id=chat_id, text='Xabarni yuboring', reply_markup=commands.back_keyboard(user.lang))
    

def send_post(bot: TeleBot, message):
    yuborildi = 0
    yuborilmadi = 0
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = None
    user.save()
    for user in BotUser.objects.all():
        try:
            # bot.forward_message(chat_id=chat_id, from_chat_id=message.forward_from_chat.id, message_id=message.forward_from_message_id)
            bot.copy_message(chat_id=user.chat_id, from_chat_id=chat_id, message_id=message.id)
            yuborildi += 1
            time.sleep(0.008)
            print(1)
        except Exception:
            print(2)
            yuborilmadi += 1
            time.sleep(0.008)
            continue

    bot.send_message(chat_id=285151723,text=f"Yuborildi {yuborildi} ta azoga \nYuborilmadi {yuborilmadi}")

def send_message_channel(bot: TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 7
    user.save()
    bot.send_message(chat_id=chat_id, text='Xabarni yuboring', reply_markup=commands.back_keyboard(user.lang))


def send_message_channel_post(bot: TeleBot, message):
    yuborildi = 0
    yuborilmadi = 0
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = None
    user.save()
    for channel in Channel.objects.all():
        try:
            # bot.forward_message(chat_id=chat_id, from_chat_id=message.forward_from_chat.id, message_id=message.forward_from_message_id)
            bot.copy_message(chat_id=channel.chat_id, from_chat_id=chat_id, message_id=message.id)
            yuborildi += 1
            time.sleep(0.008)
            print(1)
        except Exception as e:
            print(2, e)
            yuborilmadi += 1
            time.sleep(0.008)
            continue

    bot.send_message(chat_id=285151723,text=f"Yuborildi {yuborildi} ta kanalga \nYuborilmadi {yuborilmadi} ta kanalga")