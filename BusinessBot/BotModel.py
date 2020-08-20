import logging
import os
from typing import Dict, List, NamedTuple

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.webdriver import WebDriver

from BotExceptions import WebException
from currencies import RU


BOT_COMMANDS = [
    ('notify',"[валюта[время]] настройка оповещений."),
    ('notifications',"просмотр оповещений."),
    ('rate',"[валюта] вывод курса валюты по ЦБ.")
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class BotWebModel():
    """Class describes bot business logic."""
    def __init__(self):
        self._conn = self._get_connection()

    def _get_connection(self) -> WebDriver:
        """Return chromedriver web connection object (ver. 84.0.4147.30)."""
        command_executor = os.getenv('CHROME_COMMAND_EXECUTOR')
        web_options = webdriver.ChromeOptions()
        web_options.add_argument('headless') 
        try:
            conn = webdriver.Remote(command_executor,
                                    desired_capabilities=DesiredCapabilities.CHROME,
                                    options=web_options)
            logging.info('conn: open')
        except WebDriverException as exc:
            logging.error(f'WebDriverException: {exc.msg}')
        else:
            return conn
    
    def _get_conn_url(self, url: str) -> WebDriver:
        try:
            if not url:
                raise WebException(f'{url=}')
        except WebException as exc:
            logging.info(exc.text)
        else:
            try:
                self._conn.get(url)
                return self._conn
            except WebDriverException as exc:
                logging.error(f'WebDriverException: {exc.msg}')
            except AttributeError as err:
                logging.error(f'AttributeError: {err}')

    def get_element_text(self, url: str, selector: str) -> str:
        """Return text between HTML tag that has been found by selector expression.""" 
        conn_url = self._get_conn_url(url)
        try:
            return conn_url.find_element_by_css_selector(selector).text
        except AttributeError as exc:
            logging.error(f'AttributeError: {exc}')
        except WebDriverException as exc:
            logging.error(f'WebDriverException: {exc.msg}')

    def __del__(self):
        """Complete web connection."""
        try: 
            self._conn.quit()
        except WebDriverException as exc:
            logging.error(f'WebDriverException: {exc.msg}')
        except AttributeError as err:
            logging.error(f'AttributeError: {err}')
        else:
            logging.info(f'conn: quit')
            

class KeyBoard(NamedTuple):
    rows: List[list]
    mark: int

def get_keyboard(names: Dict,
                 mark: int=0,
                 height: int=2,
                 width: int=3) -> KeyBoard:
    ''' Return two-dimentional array of "names" list 
        with specified height, width and start mark of parsed array.'''
    if mark == len(names): mark = 0
    volume = (height * width) + mark
    rows = []
    row = []
    values = list(names.values())
    while not mark // volume and mark != len(names):
        row.append(str(values[mark][RU]).title())
        mark += 1
        if not mark % width or mark == len(names):
            rows.append(row)
            row = []
    result = KeyBoard(rows=rows, mark=mark)
    return result
