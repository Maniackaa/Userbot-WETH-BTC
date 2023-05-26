import re
import logging.config

from config_data.config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
err_log = logging.getLogger('errors_logger')


def convert_kilo_mega(value: str) -> int:
    """
    Конвертирует текст '201K', '20.5M' в числа
    :param value:
    :return:
    """
    try:
        result = 0
        short_nums = {'K': 1000, 'M': 1000000, 'G': 1000000000}
        for char in value:
            if char.upper() in short_nums:
                digitals = value.split(char)[0]
                print(digitals)
                result = int(float(digitals) * short_nums[char.upper()])
        return result
    except Exception:
        err_log.error(f'Ошибка распознавания: {value}')



def response_liquidation(text: str):
    """
    Распознает сообщение
    📈 #BTC Liquidated Short: $201K at $26087.90
    :param text:
    :return:
    """
    pattern = (r'^.+#(\w+)'
               r'.+'
               r'([Ss]hort|[Ll]ong)'
               r': \$(\d+\.?\d+\w)'
               r'.+\$'
               r'([\d\.]+)'
               r'$')
    search = re.search(pattern, text)
    if search:
        coin = search.group(1)
        transaction = search.group(2)
        volume = convert_kilo_mega(search.group(3))
        price = float(search.group(4))
        return coin, transaction, volume, price


# x = response_liquidation('📈 #BTC Liquidated Short: $201K at $26087.90')
# print(x)


def response_bitmex_liquidation(text: str):
    """
    Распознает сообщение
    🔴 Liquidated Long: 114K contracts at $26,958
    :param text:
    :return: transaction: str, volume: int, price: float
    """
    pattern = (r'^.+([Ss]hort|[Ll]ong)'
               r': '
               r'(\d+\.?\d+\w)'
               r'.+\$'
               r'([\d\S]+)'
               r'$')
    search = re.search(pattern, text)
    if search:
        transaction = search.group(1)
        volume = convert_kilo_mega(search.group(2))
        price = float(search.group(3).replace(',', ''))
        return transaction, volume, price

