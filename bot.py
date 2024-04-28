import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv(".env")

# Получение переменных окружения
token = str(os.getenv('TOKEN'))
threshold = float(os.getenv('THRESHOLD'))
timeout = float(os.getenv('TIMEOUT'))
info = f"timeout = {timeout} sec\n treashold (price change) = {threshold}"


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time


old_price = info
async def send_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global old_price
    chat_id = update.message.chat_id
    price = info
    while True:
        copared = compare_price(price, old_price)
        if copared:
            await context.bot.send_message(chat_id=chat_id, text=str(price))
        old_price = price
        price = parse_price()
        time.sleep(timeout)  


def compare_price(price, old_price):
    try:
        price = float(price)
        old_price = float(old_price)
        current_changes = abs((old_price-price)/old_price)
        if current_changes >= threshold:
            return True
        else:
            return False
    except:
        return True
        

def parse_price():
    import requests
    from lxml import html

    # URL веб-сайта
    url = 'https://www.bestchange.ru/sberbank-to-tether-bep20.html'

    # Получение HTML страницы
    response = requests.get(url)
    if response.status_code == 200:
        # Парсинг HTML
        tree = html.fromstring(response.content)
        
        # XPath для поиска нужной части HTML
        xpath = '//*[@id="content_table"]/tbody'
        
        # Поиск элемента по XPath
        element = tree.xpath(xpath)
        
        # Проверка наличия элемента и вывод его HTML
        if element:
            # Получение HTML элемента
            html_content = html.tostring(element[0]).decode('utf-8')
            
            # Парсинг HTML
            tree = html.fromstring(html_content)

            # XPath для поиска элемента, содержащего значение
            rate = tree.xpath('//td[@class="bi"]/div[@class="fs"]/text()')[0].strip()

            return rate
        else:
            return ("Элемент по заданному XPath не найден.")
    else:
        return (f"Ошибка: Не удалось получить данные, статус-код {response.status_code}")

def main() -> None:
    application = Application.builder().token(token).build()

    # Команда start, чтобы начать отправлять числа
    start_handler = CommandHandler('start', send_number)
    application.add_handler(start_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
