import asyncio
import json
import time
import aiohttp
from bs4 import BeautifulSoup
from constants import headers
from secondary_classes import MyEncoder
from secondary_function import store, getFullURL, league_init, club_init, clubs_leagues_init, get_pagination_leagues
from config import *


async def get_data_from_region_page(session, url):
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        leagues_page = soup.find_all(class_='inline-table')

        for league in leagues_page:
            id = league.find('tr').contents[-2].find('a').get('href').split('/')[-1]
            link = getFullURL(league.find('tr').contents[-2].find('a').get('href'))
            name = league.find('tr').contents[-2].find('a').get('title')
            store['leagues'][id] = league_init(id)
            store['leagues'][id]['id'] = id
            store['leagues'][id]['name'] = name
            store['leagues'][id]['link'] = link


async def get_data_from_league_page(session, url):
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        league_id = url.split('/')[-1]
        try:
            if soup.find(class_='data-header__info-box').text.find('Тип кубка') != -1:
                store['leagues'].pop(league_id)
                return
        except AttributeError as AE:
            logging.info(AE, url)

        try:
            logo = soup.find(class_='data-header__profile-container').find('img').get('src')
            store['leagues'][league_id]['logo'] = logo
        except Exception as ex:
            logging.info(f'нет logo для {url}')

        try:
            country_id = soup.find(class_='data-header__club').find('a').get('href').split('/')[-1]
            store['leagues'][league_id]['country_id'] = country_id
        except Exception as ex:
            logging.info(f'нет country_id для {url}')

        try:
            leagues_info = soup.find_all(class_='data-header__label')
            for league in leagues_info:
                if league.text.strip().find('Рейтинг') != -1:
                    level = league.text.split(':')[-1].strip()
                    store['leagues'][league_id]['level'] = level
                if league.text.strip().find('Действующий') != -1:
                    champion_club_id = league.find('a').get('href').split('/')[-1]
                    store['leagues'][league_id]['champion_club_id'] = champion_club_id
                if league.text.strip().find('Коэффициент') != -1:
                    uefa_pos = league.find('a').text.split('.')[0]
                    uefa_points = float(league.find('span').find('span').text)
                    store['leagues'][league_id]['uefa_pos'] = uefa_pos
                    store['leagues'][league_id]['uefa_points'] = uefa_points
        except Exception as ex:
            logging.info(f'нет блока с инфой {url}')

        try:
            clubs = soup.find(class_='items').find_all(class_='hauptlink no-border-links')
            for club in clubs:

                name = club.find('a').text
                link = club.find('a').get('href')
                club_id = link.split('/')[-3]

                if club_id is not None and club_id not in store['clubs'].keys():
                    store['clubs'][club_id] = club_init(club_id)
                    store['clubs'][club_id]['id'] = club_id
                    store['clubs'][club_id]['name'] = name
                    store['clubs'][club_id]['link'] = getFullURL(link)

                clubs_leagues_id = str(club_id) + '-' + str(league_id)
                store['clubs_leagues'][clubs_leagues_id] = clubs_leagues_init()
                store['clubs_leagues'][clubs_leagues_id]['club_id'] = club_id
                store['clubs_leagues'][clubs_leagues_id]['league_id'] = league_id

        except Exception as ex:
            logging.info(f'Список клубов не найден {url}')


async def gather_data_region(url):
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []

        for page in range(1, get_pagination_leagues(url) + 1):
            new_url = f'{url}?page={page}'
            task = asyncio.create_task(get_data_from_region_page(session, new_url))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def gather_data_league():
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        urls = ['https://www.transfermarkt.world/o21-divisie-2-fall/startseite/wettbewerb/212F',
                'https://www.transfermarkt.world/o21-divisie-1-spring/startseite/wettbewerb/211S']
        for url in urls:
            task = asyncio.create_task(get_data_from_league_page(session, url))
            tasks.append(task)
        # tasks = []
        # for id in store['leagues']:
        #     url = store['leagues'][id]['link']
        #     task = asyncio.create_task(get_data_from_league_page(session, url))
        #     tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    tym = time.localtime()
    start_time = time.time()
    current_date_and_time = time.strftime("%d/%m/%Y, %H:%M:%S", tym)
    logging.info(f"Cкрипт начал работу в {current_date_and_time}")
    url = 'https://www.transfermarkt.world/wettbewerbe/europa'

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data_region(url))
    asyncio.run(gather_data_league())

    json.dump(store, open(r'C:\Users\reshi\Projects\pythonProject\transfers\store.json', 'w', encoding='utf-8'),
              indent=2,
              ensure_ascii=False, cls=MyEncoder)  # fsdf

    finish_time = time.time() - start_time
    logging.info(f"Затраченное на работу скрипта время: {finish_time}s\n")


if __name__ == "__main__":
    main()
