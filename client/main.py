from telebot import TeleBot

import config
import commands, info, admin
import handlers, states
from call_types import CallTypes

from backend.models import BotUser, Information
from backend.templates import Messages, Keys

message_handlers = {
    '/start': commands.start_command_handler,
    '/admin': admin.admin_commands_handler,
}

key_handlers = {
    Keys.YES: handlers.send_message_channel,
    Keys.NO: commands.main_command_handler,
    Keys.BACK: commands.main_command_handler,
    Keys.SEND_MESSAGE: admin.rassilka_commands_handler,
    Keys.SEND_MESSAGE_CHANNEL: admin.send_message_channel,
    Keys.STATISTICS: admin.statistics_commands_handler
}

state_handlers = {
    '1': states.add_channel,
    '2': handlers.send_photo_video_file_handler,
    '3': handlers.send_me_message_text,
    '4': handlers.button_message_handlers,
    '5': handlers.choices_channel,
    '6': admin.send_post,
    '7': admin.send_message_channel_post,
}

bot = TeleBot(
    token=config.TOKEN,
    num_threads=3,
    parse_mode='HTML',
)


print(bot.get_me())
def create_user(message) -> BotUser:
    return BotUser.objects.create(
        chat_id=message.chat.id,
        full_name=message.chat.first_name,
    )


@bot.message_handler()
def message_handler(message):
    print(message.content_type)
    chat_id = message.chat.id
    if not BotUser.objects.filter(chat_id=chat_id).exists():
        create_user(message)

    user = BotUser.objects.get(chat_id=chat_id)
    if Keys.BACK.get(user.lang)==message.text:
        commands.main_command_handler(bot, message)
        return
    if user.bot_state:
        if user.bot_state == '3':
            info = Information.objects.filter(user=user).last()
            handlers.send_me_message_text(bot, message, info.id)
            return
        elif user.bot_state == '4':
            info = Information.objects.filter(user=user).last()
            handlers.button_message_handlers(bot, message, info.id)
            return
        elif user.bot_state == '5':
            info = Information.objects.filter(user=user).last()
            handlers.choices_channel(bot, message, info.id)
            return
        state_handlers[user.bot_state](bot, message)
        return

    for text, handler in message_handlers.items():
        if message.text == text:
            handler(bot, message)
            return

    for key, handler in key_handlers.items():
        if message.text in Keys.YES.getall():
            info = Information.objects.filter(user=user).last()
            handlers.send_message_channel(bot, message, info.id)
            return
        if message.text in key.getall():
            handler(bot, message)
            return

    text = Messages.NOT_EXISTS_MSG.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text)

@bot.message_handler(content_types=['audio', 'document', 'photo', 'sticker', 'video'])
def message_handlers1(message):
    chat_id = message.chat.id
    if not BotUser.objects.filter(chat_id=chat_id).exists():
        create_user(message)
    user = BotUser.objects.get(chat_id=chat_id)
    if user.bot_state:
        if user.bot_state == '3':
            info = Information.objects.filter(user=user).last()
            handlers.send_me_message_text(bot, message, info.id)
            return
        state_handlers[user.bot_state](bot, message)
        return

callback_query_handlers = {
    CallTypes.Language: handlers.language_callback_query_handler,
    CallTypes.SendMessage: handlers.send_message_handler,
    CallTypes.Back: commands.back_call_handler,
    CallTypes.AddChannel: handlers.add_channel_handler,
    CallTypes.AddFile: handlers.add_file_handler,
    CallTypes.ChannelName: handlers.choice_channel,
    CallTypes.ButtonName: handlers.button_click,
    # CallTypes.AddFileNo

    CallTypes.Info: info.bot_info_message,
    CallTypes.Channels: handlers.channels_handlers,
    CallTypes.Posts: handlers.posts_user,
    CallTypes.DeletePost: handlers.delete_post,
    CallTypes.Active: commands.active_post,
    CallTypes.SeeVoted: commands.see_voted_post,
}


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, handler in callback_query_handlers.items():
        print(call_type.__class__ == CallTypes.ButtonName)
        if call_type.__class__ == CallTypes.ChannelName:
            chat_id = call.from_user.id
            user = BotUser.objects.get(chat_id=chat_id)
            info = Information.objects.filter(user=user).last()
            handlers.choice_channel(bot, call, info.id)
            break
        elif CallType == call_type.__class__:
            handler(bot, call)
            break


if __name__ == "__main__":
    # bot.polling()
    bot.infinity_polling()