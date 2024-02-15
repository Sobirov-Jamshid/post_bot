from telebot import TeleBot, types

from backend.templates import Messages, Smiles, Keys
from backend.models import BotUser, Information, Vote, File, Voting

import utils, handlers
from call_types import CallTypes


def start_command_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    uz_language_button = utils.make_inline_button(
            text=Keys.LANGUAGE.get(BotUser.Lang.UZ),
            CallType=CallTypes.Language,
            lang=BotUser.Lang.UZ,
        )
    ru_language_button = utils.make_inline_button(
        text=Keys.LANGUAGE.get(BotUser.Lang.RU),
        CallType=CallTypes.Language,
        lang=BotUser.Lang.RU,
        )
    en_language_button = utils.make_inline_button(
        text=Keys.LANGUAGE.get(BotUser.Lang.EN),
        CallType=CallTypes.Language,
        lang=BotUser.Lang.EN,
        )
    keyboard.add(uz_language_button)
    keyboard.add(ru_language_button)
    keyboard.add(en_language_button)
    text = Messages.START_COMMAND.get(BotUser.Lang.UZ)
    bot.send_message(chat_id, text, reply_markup=keyboard)


def back_call_handler(bot: TeleBot, call):
    call.message.edited = True
    user = BotUser.objects.get(chat_id=call.message.chat.id)
    user.bot_state = None
    user.save()
    handlers.menu_command_handler(bot, call)

def back_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Keys.BACK.get(lang))
    return keyboard


def main_command_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = None
    user.save()
    keyboard = types.ReplyKeyboardRemove()
    keyboard = handlers.menu_keyboard(user.lang)
    text = Messages.MAIN_COMMAND_HANDLER.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

def active_post(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    id = call_type.id
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    info = Information.objects.get(id=id)
    if info.active == True:
        info.active = False
        info.save()
    else:
        info.active = True
        info.save()
    vote = Vote.objects.filter(information=info)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    post_status = utils.make_inline_button(
        text=Keys.POST_STATUS.get(user.lang),
        CallType=CallTypes.Nothing
    )
    if info.active == True:
        active = utils.make_inline_button(
            text=Keys.ACTIVE.get(user.lang),
            CallType=CallTypes.Active,
            id=info.id
        )
    else:
        active = utils.make_inline_button(
            text=Keys.DEACTIVATE.get(user.lang),
            CallType=CallTypes.Nothing
        )

    keyboard.add(post_status, active)
    for button in vote:
        keyboard.add(
            utils.make_inline_button(
                text=f"{button.title} {button.count}",
                CallType=CallTypes.ButtonName,
                info_id=info.id,
                id=button.id
            )
        )
    text = info.body
    file = File.objects.get(information=info)
    if file.type == 'text':
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)
    else:
        bot.edit_message_caption(caption=text, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)
        

def see_voted_post(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    id = call_type.id
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    info = Information.objects.get(id=id)
    voting = Voting.objects.filter(information=info)
    text = Messages.VOTING_POSTS.get(user.lang)
    text += '\n'
    if voting.exists():
        son = 0
        for i in voting:
            son += 1
            text += Messages.USER_VOTING.text.format(id=son, chat_id=i.chat_id, full_name=i.full_name) + '\n'
        print(text)
        bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    else:
        text = Messages.NOT_VOTING.get(user.lang)
        bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)