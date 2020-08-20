from typing import Dict, List, NamedTuple

import db
from BotExceptions import CurrencyException


class WebSet(NamedTuple):
    selector: str
    url: str
    symbol: str
    unit: int

RU, EN = range(2)

class Currencies():

    def __init__(self):
        self._currencies = self._load_currencies()
        self._currencies_names = self._load_currencies_names()
    
    def _load_currencies(self) -> Dict:
        cursor = db.get_cursor()
        cursor.execute(
            ''' SELECT  v.id_currency_index, v.currency_unit, v.symbol,
                        i.id_index_selector, i.url
                FROM currency_index v
                LEFT JOIN index_selector i 
                    ON i.currency_index_id = id_currency_index
                LEFT JOIN burse b 
                    ON b.url = i.url 
                    AND LOWER(b.name) = "mainfin"; ''')
        rows = cursor.fetchall()
        currencies = {}
        currency_index, currency_unit, symbol, selector, url = range(5)
        for row in rows:
            currency = row[currency_index]
            webset = WebSet(selector=row[selector],
                            url=row[url],
                            symbol=row[symbol],
                            unit=row[currency_unit])
            currencies[currency] = webset
        return currencies

    def _load_currencies_names(self) -> Dict:
        '''Return all currency names with links.'''
        cursor = db.get_cursor()
        cursor.execute(
            ''' SELECT ci.`id_currency_index`, ci.`name` FROM currency_index ci
                LEFT JOIN index_selector i ON i.currency_index_id = id_currency_index
                LEFT JOIN burse b ON b.url = i.url AND LOWER(b.name) = "mainfin"
                UNION ALL
                SELECT il.`currency_index_id`, il.`id_index_link` FROM index_link il
                LEFT JOIN currency_index ci ON ci.id_currency_index = il.currency_index_id
                LEFT JOIN index_selector i ON i.currency_index_id = il.currency_index_id
                LEFT JOIN burse b ON b.url = i.url AND LOWER(b.name) = "mainfin"; '''
        )
        rows = cursor.fetchall()
        currency_index, currency_name = range(2)
        result = {}
        for row in rows:
            index = row[currency_index]
            if not index in result.keys():
                result[index] = list()
            result[index].append(row[currency_name].lower())
        return result

    def get_currencies_names(self) -> List[str]:
        return self._currencies_names

    def get_index(self, currency: str) -> str:
        currencies = self._currencies_names
        for index in currencies:
            if currency.lower() in currencies[index] \
            or currency.upper() == index:
                return index

    def get_webset(self, currency: str) -> WebSet:
        index = self.get_index(currency)
        if index:
            return self._currencies[index]

    def get_name(self, currency: str, lan: str=RU) -> str:
        index = self.get_index(currency)
        if index:
            return self._currencies_names[index][lan].title()

    # def is_currency(self, currency) -> bool:
    #     return isinstance(self._get_index(currency), int)
    

        