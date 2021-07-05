from enum import Enum


class FlashMessageCategory(Enum):
    SUCCESS = 'green'
    ERROR = 'red'
    MESSAGE = 'black'


class FilterStatus(Enum):
    ACTIVE = 'active'
    FINISHED = 'finished'
    ALL = 'all'
