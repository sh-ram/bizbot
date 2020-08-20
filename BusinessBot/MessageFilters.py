import re
from typing import Dict

from telegram.ext import Filters

class Patterns:
    NOTIFY_FORCE = 'notify_force'
    NOTIFY_DISABLE = 'notify_disable'
    RATE_MASK = 'rate_mask'
    CURRENCY_MASK = 'currency_mask'
    CURRENCY = 'currency'
    CURRENCY_SHOW_MORE = 'currency_show_more'
    TIME_CONV = 'time_conversation'
    FALLBACK = 'fallback'

patterns = {
    'notify_force': r''' ^/notify
            (?#currency 1)\s*([^0-9\s]+(?:\s*[^0-9\s]+)?)\s*
            (?#hours 2)   ([\d]{1,2})
            (?#minutes 3) (?::([\d]{1,2}))?
            (?#seconds 4) (?::([\d]{1,2}))? ''',

    'notify_disable': r'(?<=^/notify)\w{3}(?=_$)|(?<=/notify)(?=_$)',
    'rate_mask': r'/rate(?:\s*[^0-9\s]+)+',
    'currency_mask': r'/notify\s*(?:[^0-9\s]+\s*)+',
    'currency': r'''(?<=\s)?(?<![^0-9\s])(?!\s|/|\d) 
                    [^0-9\s:_-]+
                    (?:\s[^0-9\s/]+)?
                    | (?<=/notify) [^0-9\s]+
                    | (?<=/rate) [^0-9\s]+ ''',

    'currency_show_more': 'еще',
    'time_conversation': r'''
    (?# hours)              (
        (?# at start)        ^(?:[\d]{1,2})
        (?# after any text)  | (?:(?<=\s|[aA-zZаА-яЯ]) (?<!:\s|\d\s) [\d]{1,2})
                            ) :?
    (?# minutes)            ((?<=:)\d{1,2})? :?
    (?# seconds)            ((?<=:)\d{1,2})? ''',

    'fallback': r'(?<=^/)?(?:отмена|cancel)',
}

class ReFilter(Filters.regex):

    def __init__(self, pattern):
        if isinstance(pattern, str):
            pattern = re.compile(patterns[pattern], re.I | re.X)
        super().__init__(pattern)
    
    def filter(self, message):
        return super().filter(message)

class Regex():

    def match(self, pattern: str, text: str) -> str:
        if isinstance(pattern, str):
            if pattern in patterns.keys():
                pattern = patterns[pattern]
            pattern = re.compile(pattern, re.X | re.I)
        matches = pattern.findall(text)
        if matches:
            return matches[0]
    
    def is_match(self, pattern: str, text: str) -> bool:
        return isinstance(self.match(pattern, text), str)