from enum import Enum


class Commands(str, Enum):
    START = 'start'
    HELP = 'help'
    HELP_GROUP_CHAT = 'help_group_chat'
    RETRY = 'retry'
    NEW = 'new'
    CANCEL = 'cancel'
    MODE = 'mode'
    SETTINGS = 'settings'
    BALANCE = 'balance'

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)
