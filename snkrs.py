# -*- coding: utf-8 -*-

import webdriver_manager.chrome
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import telegram
import time


telegram_api = "5286681306:AAHyisBsFnHAek-UD3NaIzjtL4c2RdgtuK0"
chat_id = '-1001570623324'
bot = telegram.Bot(token=telegram_api)

if __name__ == '__main__':
    today = datetime.today()
    year = today.year
    month = today.month
    day = today.day
    hour = today.hour
    minute = today.minute

    today_str = f'{year}년 {month}월 {day}일'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    url = 'https://www.nike.com/kr/launch/?type=upcoming'
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    upcoming_div = soup.find('div', attrs={'class': 'launch-category ncss-container feed-container-inner'})
    upcoming_lists = upcoming_div.find_all('li', attrs={'class': 'pb2-sm'})

    if len(upcoming_lists) == 0:
        raise Exception('새로 출시 예정인 드로우가 없습니다.')

    draw_list = []
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

        draw_dict = {
            'product_name': product_name,
            'product_link': product_link,
            'img_src': img_src,
            'release_month': release_month,
            'release_day': release_day,
        }
        draw_list.append(draw_dict)

    draw_df = pd.DataFrame(draw_list)

    today_draw = draw_df.loc[(draw_df['release_month']==month) & (draw_df['release_day']==day)]
    else_draw = draw_df.loc[~draw_df.index.isin(today_draw.index)]

    if today_draw.empty:
        raise Exception("오늘 오픈하는 드로우가 없습니다.")

    for i, row in today_draw.iterrows():
        sending_message = f'{row["release_month"]}월 {row["release_day"]}일\n' \
                          f'<strong>{row["release_time"]}시 응모 시작!</strong>\n' \
                          f'\n' \
                          f'- 상품먕: <a href="{row["product_link"]}">{row["product_name"]}</a>'
        bot.sendPhoto(chat_id=chat_id, photo=img_src, caption=sending_message, parse_mode='HTML')
    if len(else_draw) > 0:
        upcoming_list = [f'* {r["release_month"]}월 {r["release_day"]}일: {r["product_name"]}'
                         for i, r in else_draw.iterrows()]
        future_draw_message = f'다음 드로우 일정은...\n'
        for i, upcoming in enumerate(upcoming_list):
            future_draw_message += upcoming + '\n'
        future_draw_message += '입니다.\n' \
                               '그 날 다시 알려드릴게요! 그럼 다음에 만나요~ :)'
        bot.sendMessage(chat_id=chat_id, text=future_draw_message)

    driver.close()

