from telebot import TeleBot, types

from backend.models import BotUser, Channel, File, Vote, Information, Voting
from backend.templates import Messages, Keys, Smiles
from call_types import CallTypes
import utils

def language_callback_query_handler(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    lang = call_type.lang
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.lang = lang
    user.save()
    menu_command_handler(bot, call)

def back_keyboard(user):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        utils.make_inline_button(
            text=Keys.BACK.get(user.lang),
            CallType=CallTypes.Back
        )
    )
    return keyboard


def menu_keyboard(lang):
    keyboard = types.InlineKeyboardMarkup()
    post = utils.make_inline_button(
        text=Keys.POSTS.get(lang),
        CallType=CallTypes.Posts
    )
    send_message = utils.make_inline_button(
        text=Keys.SEND_MESSAGE.get(lang),
        CallType=CallTypes.SendMessage
    )
    add_channel = utils.make_inline_button(
        text=Keys.ADD_CHANNEL.get(lang),
        CallType=CallTypes.AddChannel
    )
    # info_button = utils.make_inline_button(
    #     text=Keys.INFO.get(lang),
    #     CallType=CallTypes.Info,
    # )
    channels = utils.make_inline_button(
        text=Keys.CHANNELS.get(lang),
        CallType=CallTypes.Channels
    )

    keyboard.add(post, send_message)
    keyboard.add(channels, add_channel)
    # keyboard.add(info_button)
    return keyboard

def menu_command_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    lang = user.lang
    keyboard = menu_keyboard(lang)
    text = Messages.MENU_COMMAND.get(lang)
    bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)


def send_message_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    keyboard = types.InlineKeyboardMarkup()
    if Channel.objects.filter(user=user).exists():
        keyboard.add(
            utils.make_inline_button(
                text=Keys.YES.get(user.lang),
                CallType=CallTypes.AddFile,
                yes='yes',
            ),
            utils.make_inline_button(
                text=Keys.NO.get(user.lang),
                CallType=CallTypes.AddFile,
                yes='no',
            )
        )
        keyboard.add(
            utils.make_inline_button(
                text=Keys.BACK.get(user.lang),
                CallType=CallTypes.Back
            )
        )
        text = Messages.SEND_MEDIA.get(user.lang)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id,reply_markup=keyboard)
    else:
        keyboard.add(
            utils.make_inline_button(
                text=Keys.ADD_CHANNEL.get(user.lang),
                CallType=CallTypes.AddChannel
                ),
            utils.make_inline_button(
                text=Keys.BACK.get(user.lang),
                CallType=CallTypes.Back
                )
        )
        text = Messages.NO_CHANNEL.get(user.lang)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)

def add_channel_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 1
    user.save()
    channel = Channel.objects.filter(user=user)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            text=Keys.ADD_TO_CHANNEL.get(user.lang),
            url='https://t.me/{bot}?startchannel='.format(bot=bot.get_me().username),
        ),
        utils.make_inline_button(
            text=Keys.BACK.get(user.lang),
            CallType=CallTypes.Back
        )
    )
    text = Messages.ADD_TO_CHANNEL.get(user.lang)
    bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=keyboard)

def channels_handlers(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 1
    user.save()
    channel = Channel.objects.filter(user=user)
    print(channel)
    if channel.exists():
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for channel in channel:
            keyboard.add(
                utils.make_inline_button(
                    text=channel.title,
                    CallType=CallTypes.ChannelName,
                    id=channel.id
                ),
                utils.make_inline_button(
                    text=Keys.DELETE_POST.text,
                    CallType=CallTypes.DeletePost,
                    id=channel.id
            )
            )
        keyboard.add(
            utils.make_inline_button(
                text=Keys.BACK.get(user.lang),
                CallType=CallTypes.Back
            )
        )
        text = Messages.MESSAGE_CHANNEL.get(user.lang)
        bot.edit_message_text(chat_id=chat_id, text=text, message_id=call.message.id, reply_markup=keyboard)
    else:
        add_channel_handler(bot, call)

def delete_post(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    id = call_type.id
    channel = Channel.objects.filter(id=id).delete()
    channels_handlers(bot, call)

def add_file_handler(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    yes = call_type.yes
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 2
    user.save()
    if yes =='yes':
        text = Messages.SEND_ME_FILE_MESSAGE.get(user.lang)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=back_keyboard(user))
    else:
        text = Messages.SEND_ME_TEXT_MESSAGE.get(user.lang)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.id, reply_markup=back_keyboard(user))

def send_photo_video_file_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 3
    user.save()
    info = Information.objects.create(user=user, body='text')

    if message.content_type == 'photo':
        file = File.objects.create(information=info, type=message.content_type ,file_id=message.photo[2].file_id)

    elif message.content_type == 'video':
        file = File.objects.create(information=info, type=message.content_type ,file_id=message.video.file_id)

    elif message.content_type == 'document':
        file = File.objects.create(information=info, type=message.content_type ,file_id=message.document.file_id)

    elif message.content_type == 'audio':
        file = File.objects.create(information=info, type=message.content_type ,file_id=message.audio.file_id)

    elif message.content_type == 'text':
        file = File.objects.create(information=info, type=message.content_type)
        send_me_message_text(bot, message, info.id)
        return
        
    text = Messages.SEND_ME_TEXT_MESSAGE.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=back_keyboard(user))
    

def send_me_message_text(bot: TeleBot, message, id):
    chat_id = message.chat.id
    text = message.text
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 4
    user.save()
    info = Information.objects.get(id=id)
    info.body = text
    info.save()
    text = Messages.BUTTON_MESSAGE.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text)
    
def button_message_handlers(bot: TeleBot, message, id):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = 5
    user.save()
    info = Information.objects.get(id=id)
    buttons = message.text.split('*')
    for button in buttons:
        Vote.objects.create(information=info, title=button)

    channel = Channel.objects.filter(user=user)
    print(channel)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for channel in channel:
        keyboard.add(
            utils.make_inline_button(
                text=channel.title,
                CallType=CallTypes.ChannelName,
                id=channel.id
            )
        )
        
    keyboard.add(utils.make_inline_button(
            text=Keys.BACK.get(user.lang),
            CallType=CallTypes.Back
        ))
    text = Messages.CHOICES_CHANNEL.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

def choice_channel(bot: TeleBot, call, info_id):
    call_type = CallTypes.parse_data(call.data)
    id = call_type.id
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    channel = Channel.objects.get(id=id)
    information = Information.objects.get(id=info_id)
    information.channel = channel
    information.save()
    text = Messages.CHANNEL_ADDED_MESSAGE.get(user.lang)
    bot.delete_message(chat_id=chat_id, message_id=call.message.id)
    bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)
    choices_channel(bot, message=call.message, id=info_id)

def choices_channel(bot: TeleBot, message, id):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    user.bot_state = None
    user.save()
    info = Information.objects.get(id=id)
    keyboard = types.InlineKeyboardMarkup()
    vote = Vote.objects.filter(information=info)
    for button in vote:
        keyboard.add(
            utils.make_inline_button(
                text=f"{button.title} {button.count}",
                CallType=CallTypes.ButtonName,
                info_id=id,
                id=button.id
            )
        )
    text = info.body
    file = File.objects.get(information=info)
    if file.type == 'text':
        bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    elif file.type == 'photo':
        bot.send_photo(chat_id=chat_id, photo=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'video':
        bot.send_video(chat_id=chat_id, video=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'document':
        bot.send_document(chat_id=chat_id, document=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'audio':
        bot.send_audio(chat_id=chat_id, audio=file.file_id, caption=text, reply_markup=keyboard)
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton(
            text=Keys.YES.get(user.lang),
        ),
        types.KeyboardButton(
            text=Keys.NO.get(user.lang),
        ),
    )
    text = Messages.EXAMPLE_MESSAGE.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    
def send_message_channel(bot: TeleBot, message, id):
    keyboard = types.ReplyKeyboardRemove()
    chat_id = message.chat.id
    # bot.delete_message(chat_id, message.id)
    # bot.delete_message(chat_id, message.id-1)
    # bot.delete_message(chat_id, message.id-2)

    user = BotUser.objects.get(chat_id=chat_id)
    info = Information.objects.get(id=id)
    keyboard = types.InlineKeyboardMarkup()
    vote = Vote.objects.filter(information=info)
    for button in vote:
        keyboard.add(
            utils.make_inline_button(
                text=f"{button.title} {button.count}",
                CallType=CallTypes.ButtonName,
                info_id=id,
                id=button.id
            )
        )
    text = info.body
    file = File.objects.get(information=info)
    if file.type == 'text':
        bot.send_message(chat_id=info.channel.chat_id, text=text, reply_markup=keyboard)
    elif file.type == 'photo':
        bot.send_photo(chat_id=info.channel.chat_id, photo=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'video':
        bot.send_video(chat_id=info.channel.chat_id, video=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'document':
        bot.send_document(chat_id=info.channel.chat_id, document=file.file_id, caption=text, reply_markup=keyboard)
    elif file.type == 'audio':
        bot.send_audio(chat_id=info.channel.chat_id, audio=file.file_id, caption=text, reply_markup=keyboard)
    text = Messages.SEND_MESSAGE_CHANNEL.get(user.lang)
    bot.send_message(chat_id=chat_id, text=text)

def button_click(bot: TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    id = call_type.id
    info_id = call_type.info_id
    chat_id = call.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    status = ['creator', 'administrator', 'member']
    print(call.from_user.last_name)
    if bot.get_chat_member(chat_id=call.message.chat.id, user_id=chat_id).status in status:
        
        info = Information.objects.get(id=info_id)
        vote = Vote.objects.get(id=id)
        if info.active == True:
            if not Voting.objects.filter(chat_id=chat_id, information=info).exists():
                vote.count += 1
                vote.save()
                
                if call.from_user.last_name == None:
                    full_name=call.from_user.first_name
                else:
                    full_name = call.from_user.first_name+call.from_user.last_name
                Voting.objects.create(chat_id=chat_id, full_name=full_name, information=info)
                vote = Vote.objects.filter(information=info)
                
                for button in vote:
                    keyboard.add(
                        utils.make_inline_button(
                            text=f"{button.title} {button.count}",
                            CallType=CallTypes.ButtonName,
                            info_id=info_id,
                            id=button.id
                        )
                    )
                print(keyboard)
                text = info.body
                file = File.objects.get(information=info)
                if file.type == 'text':
                    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


                elif file.type == 'photo':
                    bot.edit_message_media(
                        media=types.InputMediaPhoto(
                            media=file.file_id, 
                            caption=text,
                            parse_mode='HTML'
                        ), 
                        chat_id=call.message.chat.id, 
                        message_id=call.message.id, 
                        reply_markup=keyboard
                    )
                elif file.type == 'video':
                    bot.edit_message_media(
                        media=types.InputMediaVideo(
                            media=file.file_id, 
                            caption=text,
                            parse_mode='HTML'
                        ), 
                        chat_id=call.message.chat.id, 
                        message_id=call.message.id, 
                        reply_markup=keyboard
                    )
                elif file.type == 'document':
                    bot.edit_message_media(
                        media=types.InputMediaDocument(
                            media=file.file_id,
                            caption=text,
                            parse_mode='HTML'
                        ), 
                        chat_id=call.message.chat.id, 
                        message_id=call.message.id, 
                        reply_markup=keyboard
                    )
                elif file.type == 'audio':
                    bot.edit_message_media(
                        media=types.InputMediaAudio(
                            media=file.file_id, 
                            caption=text,
                            parse_mode='HTML'
                        ), 
                        chat_id=call.message.chat.id, 
                        message_id=call.message.id, 
                        reply_markup=keyboard
                    )
            else:
                text = Messages.EXISTS_VOTING.get('uz')
                bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)
        else:
            text = Messages.DEACTIVATE_POST.text
            bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)
    else:
        text = Messages.GET_CHAT_MEMBER.get('uz')
        bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)


def posts_user(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    information = Information.objects.filter(user=user)
    if information.exists():
        for info in information:
            try:
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
                keyboard.add(
                    utils.make_inline_button(
                        text=Keys.SEE_VOTED.get(user.lang),
                        CallType=CallTypes.SeeVoted,
                        id = info.id
                        )
                )
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
                print(info, info.id)
                file = File.objects.get(information=info)
                if file.type == 'text':
                    bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
                elif file.type == 'photo':
                    bot.send_photo(chat_id=chat_id, photo=file.file_id, caption=text, reply_markup=keyboard)
                elif file.type == 'video':
                    bot.send_video(chat_id=chat_id, video=file.file_id, caption=text, reply_markup=keyboard)
                elif file.type == 'document':
                    bot.send_document(chat_id=chat_id, document=file.file_id, caption=text, reply_markup=keyboard)
                elif file.type == 'audio':
                    bot.send_audio(chat_id=chat_id, audio=file.file_id, caption=text, reply_markup=keyboard)
            except Exception as e:
                continue

    else:
        text = Messages.USER_POSTS.get(user.lang)
        bot.answer_callback_query(callback_query_id=call.id, text=text, show_alert=True)