from .models import Template


keys = Template.keys.all()
messages = Template.messages.all()
smiles = Template.smiles.all()


class Keys():
    LANGUAGE = keys[0]
    ADD_CHANNEL = keys[1]
    SEND_MESSAGE = keys[2]
    INFO = keys[3]
    YES = keys[4]
    NO = keys[5]
    BACK = keys[6]
    ADD_TO_CHANNEL = keys[7]
    STATISTICS = keys[8]
    SEND_MESSAGE = keys[9]
    SEND_MESSAGE_CHANNEL = keys[10]
    POSTS = keys[11]
    CHANNELS = keys[12]
    DELETE_POST = keys[13]
    ACTIVE = keys[14]
    DEACTIVATE = keys[15]
    POST_STATUS = keys[16]
    SEE_VOTED = keys[17]


class Messages():
    START_COMMAND = messages[0]
    MENU_COMMAND = messages[1]
    SEND_MEDIA = messages[2]
    NO_CHANNEL = messages[3]
    ADD_TO_CHANNEL = messages[4]
    NOT_ADMIN = messages[5]
    SUCCESFUL_ADDED = messages[6]
    EXISTS_CHANNEL = messages[7]
    NOT_EXISTS_MSG = messages[8]
    SEND_ME_FILE_MESSAGE = messages[9]
    SEND_ME_TEXT_MESSAGE = messages[10]
    SEND_ME_PHOTO = messages[11]
    SEND_ME_TEXT_MESSAGE = messages[12]
    BUTTON_MESSAGE = messages[13]
    EXAMPLE_MESSAGE = messages[14]
    CHOICES_CHANNEL = messages[15]
    CHANNEL_ADDED_MESSAGE = messages[16]
    SEND_MESSAGE_CHANNEL = messages[17]
    EXISTS_VOTING = messages[18]
    GET_CHAT_MEMBER = messages[19]
    BOT_INFO = messages[20]
    BOT_INFO_EXISTS = messages[21]
    ADMIN_PANEL_MESSAGE = messages[22]
    STATISTICS_MESSAGE = messages[23]
    MAIN_COMMAND_HANDLER = messages[24]
    MESSAGE_CHANNEL = messages[25]
    USER_POSTS = messages[26]
    DEACTIVATE_POST = messages[27]
    VOTING_POSTS = messages[28]
    USER_VOTING = messages[29]
    NOT_VOTING = messages[30]


class Smiles():
    STAR = smiles[0]
