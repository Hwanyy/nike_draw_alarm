# -*- coding: utf-8 -*-


from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import telegram
import time


telegram_api = "5286681306:AAHyisBsFnHAek-UD3NaIzjtL4c2RdgtuK0"
chat_id = '-1001570623324'
bot = telegram.Bot(token=telegram_api)


def get_url_info():
    driver = webdriver.Chrome('./chromedriver')
    url = 'https://www.nike.com/kr/launch/?type=upcoming'
    response = driver.get(url)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    else:
        raise Exception("SNKRS 페이지 로드에 실패하였습니다.")


if __name__ == '__main__':

    today = datetime.today()
    year = today.year
    month = today.month
    day = today.day
    today_str = f'{year}년 {month}월 {day}일'

    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://www.nike.com/kr/launch/?type=upcoming'
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main = driver.find_element_by_css_selector('body > div.main-layout > div > div.ncss-col-sm-12.full')
    upcoming_div = soup.find('div', attrs={'class': 'launch-category ncss-container feed-container-inner'})
    upcoming_lists = upcoming_div.find_all('li', attrs={'class': 'pb2-sm'})

    future_draw_list = []

    for index, list in enumerate(upcoming_lists):
        is_draw = list.find('h3').text.rfind('응모') != -1
        if not is_draw:
            continue

        product_name = list.find('h6').text
        product_link = 'nike.com/' + list.find('a').get('href')
        img_src = list.find('img').get('src')

        release_month = int(list.find('p', attrs={'data-qa': 'draw-startDate'}).text.replace('월', ''))
        release_day = int(list.find('p', attrs={'data-qa': 'draw-day'}).text)

        release_time = list.find('h3').text.split('응모')[0].strip()

        if release_month == month and release_day == day:
            sending_message = f'{release_month}월 {release_day}일\n' \
                              f'<strong>{release_time}시 응모 시작!</strong>\n' \
                              f'\n' \
                              f'- 상품먕: <a href="{product_link}">{product_name}</a>'
            bot.sendPhoto(chat_id=chat_id, photo=img_src, caption=sending_message, parse_mode='HTML')
        else:
            draw_dict = {
                '상품명': product_name,
                '상품링크': product_link,
                '상품이미지': img_src,
                '출시예정월': release_month,
                '출시예정일': release_day,
            }
            future_draw_list.append(draw_dict)

    if len(future_draw_list) > 0:
        upcoming_list = [f'{dict["출시예정월"]}월 {dict["출시예정일"]}일: {dict["상품명"]}' for dict in future_draw_list]
        future_draw_message = f'다음 드로우 일정은 다음과 같습니다.\n'
        for i, upcoming in enumerate(upcoming_list):
            future_draw_message += upcoming + '\n'
        future_draw_message = '다음 드로우 예정일에 연락드리겠습니다~ :)'
        bot.sendMessage(chat_id=chat_id, text=future_draw_message)

    driver.close()

