import datetime
import logging.config

import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import re

from config_data.config import config, LOGGING_CONFIG
from database.db import Liquidation

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('checker-sender')
err_log = logging.getLogger('errors_logger3')


def find_weth(text):
    res = re.findall('WETH liquidity: (\d+) ', text)
    return int(res[0])


def get_browser():
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=800,600")
    options.add_argument('--headless')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)


def get_check(token):
    with get_browser() as browser:
        browser.get(f'https://therugcheck.com/eth/?address={token}')
        result_xpatch = '//div[contains(text(), "Checking for Honeypot")]'
        try:
            WebDriverWait(browser, 20).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, result_xpatch)))
        except TimeoutException:
            logger.debug('Не дождался')
            result_xpatch = '//div[contains(text(), "Unable to check")]'
            result = browser.find_element(By.XPATH, result_xpatch).text
        return result


def get_rug_check(token):
    with get_browser() as browser:
        browser.set_page_load_timeout(40)
        logger.debug(f'get_browser https://therugcheck.com/eth/?address={token}')
        browser.get(f'https://therugcheck.com/eth/?address={token}')
        result_xpatch = '//div[contains(text(), "Checking for Honeypot")]'
        try:
            logger.debug('Ждем Checking for Honeypot')
            # browser.save_screenshot('honey.jpg')
            WebDriverWait(browser, 20).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, result_xpatch)))
            logger.debug('Дождались  Honeypot')
            result = browser.find_element(By.XPATH, result_xpatch).text
        except TimeoutException:
            logger.debug('Не дождался, проверяем Unable to check')
            result_xpatch = '//div[contains(text(), "Unable to check")]'
            try:
                result = browser.find_element(By.XPATH, result_xpatch).text
            except:
                browser.save_screenshot('screen_err.png')

        logger.debug(result)
        return result


def get_honeypot_check_contract(token: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://honeypot.is/',
        'Origin': 'https://honeypot.is',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    params = {
        'address': token.lower(),
        'chainID': '1',
    }

    contracts_req = requests.get(
        'https://api.honeypot.is/v1/GetContractVerification', params=params,
        headers=headers)
    if contracts_req.ok:
        contracts_json = contracts_req.json()
        print(contracts_json)
        contracts = contracts_json.get('Contracts').get(token.lower())
        return contracts
    return 'error'


def get_honeypot_check(token: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://honeypot.is/',
        'Origin': 'https://honeypot.is',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    params = {
        'address': token.lower(),
        'chainID': '1',
    }
    response = requests.get('https://api.honeypot.is/v2/IsHoneypot',
                            params=params, headers=headers)
    logger.debug(response)
    response_json = response.json()
    logger.debug(response.json())
    if response.ok:
        logger.debug(response.json())
        success = response_json.get('simulationSuccess')
        if success:
            logger.debug('success_true')
            honeypot = response_json.get('honeypotResult').get('isHoneypot')
            logger.debug(f'honeypot: {honeypot}')
            return honeypot
        else:
            logger.debug('success-false')
            return 'success-false'
    return response_json.get('error')


def send_message_tg(message: str, chat_id: str):
    """Отправка сообщения через чат-бот телеграмма"""
    logger.info(f'Отправка сообщения {chat_id} {message}')
    message = message[:2500]
    bot_token = config.tg_bot.token
    url = (f'https://api.telegram.org/'
           f'bot{bot_token}/'
           f'sendMessage?'
           f'chat_id={chat_id}&'
           f'text={message}')
    requests.get(url)


def find_start_period(
        target_day: int,
        current_day: datetime = datetime.datetime.utcnow()) -> datetime:
    """Возвращает datetime прошлонедельного заданного дня недели"""
    delta_to_day = target_day - current_day.weekday()
    if delta_to_day > 0:
        res_delta_day = 7 - delta_to_day
    else:
        res_delta_day = delta_to_day
    result_day = current_day + datetime.timedelta(days=res_delta_day)
    result_day = result_day.replace(hour=0, minute=0, second=0, microsecond=0)
    return result_day


def format_last_report(liqidations: list[Liquidation]):
    text = f'Последние 10 ликвидаций\n'
    for liqidation in liqidations:
        text += (f'{liqidation.id}. {liqidation.addet_time}\n{liqidation.source}\n'
                 f'{liqidation.text}\n'
                 )
        text += '\n'
    return text


x = find_start_period(0)
print(x)