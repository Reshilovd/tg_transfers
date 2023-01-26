import logging
import re
from constants import *
import datetime
import json
import requests
from bs4 import BeautifulSoup


def get_pagination_leagues(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    try:
        pagination = soup.find(class_='tm-pagination__list-item tm-pagination__list-item--icon-last-page').find(
            'a').get('href')
        pagination_leagues_number = int(pagination.split('=')[-1])

        return pagination_leagues_number
    except Exception as ex:
        logging.info(ex, f'Пагинация не найдена {url}')


def parsing_from_page_club(league_id, club_id, url):
    try:
        req = requests.get(url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')

        full_name = soup.find(class_='dataBild').find('img').get('alt')
        logo = soup.find(class_='dataBild').find('img').get('src')

        store[league_id][club_id]['full_name'] = full_name
        store[league_id][club_id]['logo'] = logo
        store[league_id][club_id]['url'] = url
        stadium_name, stadium_url = get_stadium_name(soup)
        stadium_id = get_stadium_id(stadium_name)
        store['stadiums'][stadium_id]['name'] = stadium_name
        store['stadiums'][stadium_id]['url'] = getFullURL(stadium_url)
        store['clubs_stadiums']

        player_url = soup.find_all(class_='di nowrap')
        for i in player_url:
            try:
                name_player = i.find(class_='show-for-small').find('a').get('title')
                url_player = getFullURL(i.find(class_='show-for-small').find('a').get('href'))
                id_player = url_player.split('/')[-1]
                store['players_link'][id_player] = url_player
                store['clubs_players'].add((id, id_player, True))
            except Exception as ex:
                print(ex)
        print('success', url)
    except Exception as ex:
        print(ex)


def parsing_player_info(id, url):
    try:
        info = {}
        req = requests.get(url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
        info['photo'] = get_photo(soup, url, id)
        info['first_name'], info['last_name'] = get_name(soup, url, id) or ['', '']
        info['birthday'] = get_birthday(soup, url, id) or '1000-01-01'
        info['death_date'] = get_death_date(soup, url, id)
        info['height'] = get_height(soup, url, id)
        info['end_career'], info['free_agent'] = get_end_career_and_free_agent(soup, url, id) or ['', '']
        info['rent_from'] = get_rent_from(soup, url, id)
        # store['clubs_players'].add((info['rent_from'], id, False))
        info['price'], info['currency'] = get_price_and_currency(soup, url, id) or ['', '']
        for nation in get_nation(soup, url, id): store['nations_players'].add(nation)
        store['positions_players'].add(get_position(soup, url, id))
        store['national_team_players'].add(get_national_team(soup, url, id))
        store['players_info'][id] = info

    except Exception as ex:
        print(ex, url)
    # time.sleep(randrange(1, 2))


def get_date(s):
    s = s.split()
    day = s[0]
    month = getMonthByName(s[1])
    year = s[2]
    date = year + month + day
    date = datetime.datetime.strptime(date, '%Y%m%d').date()
    return str(date)


def getMonthByName(s):
    monthes = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    nStr = s.lower().strip()
    for i in range(len(monthes)):
        if re.match(monthes[i], nStr) != None: return ('0' + str(i + 1))[
                                                      -2:]  # Если нашли то возвращаем номер месяца в формате 01, 02

    return None


def convert_price(price):
    price = price.split()
    coast = float(price[0].replace(',', '.'))
    coast = coast * (1_000_000 if re.match('млн', price[1]) else 1_000)
    currency = price[2]
    return int(coast), currency


def store_init():
    return {'leagues': {

    },
        'leagues_clubs': set(),

        'clubs': {

        },
        'clubs_players': set(),

        'clubs_link': {

        },
        'stadiums': {

        },
        'stadium_clubs': set(),

        'players_link': {

        },
        'players_info': {

        },
        'positions': [],
        'positions_players': set(),

        'nation': [],
        'nations_players': set(),

        'national_team_players': set()

    }


def club_init(id):
    return {
        'id': '',
        'name': '',
        'link': '',
        'logo': ''
    }


def league_init(id):
    return {
        'id': '',
        'name': '',
        'level': '',
        'uefa_pos': 0,
        'uefa_points': 0,
        'champion_club_id': '',
        'country_id': '',
        'link': '',
        'logo': '',
    }


def player_init(id):
    return {
        'name': '',
        'logo': '',
    }


def clubs_leagues_init():
    return {
        'club_id': '',
        'league_id': '',
    }


getFullURL = lambda url: f"https://www.transfermarkt.ru{url}"


def logger(func):
    def wrapper(soup, url):
        try:
            res = func(soup, url)
            return res
        except Exception as ex:
            template = "\n##########################"
            template += "\n" + str(datetime.datetime.now())
            template += "\nURL: " + url
            template += "\nФункция: " + func.__name__
            template += "\nОшибка типа: {0}.\nАргументы: {1}"
            message = template.format(type(ex).__name__, ex.args)
            file = open('log/log.txt', 'a+')
            file.write(message)
            file.close()
            return ""

    return wrapper


@logger
def get_photo(soup, url):
    return soup.find(class_="modal-trigger").find('img').get('src')


@logger
def get_name(soup, url):
    name = soup.find(class_='dataName')
    last_name = name.find('b').text
    first_name = ' '.join(filter(lambda x: not x in last_name.split(), name.find('h1').text.split()))
    return first_name, last_name


@logger
def get_birthday(soup, url):
    # store['players_info'][id]['birthday'] = '1000-01-01'
    birthday = soup.find(class_='dataValue').text.split()
    day = birthday[0]
    month = getMonthByName(birthday[1])
    year = birthday[2]
    date = year + month + day
    date = datetime.datetime.strptime(date, '%Y%m%d').date()
    return str(date)


@logger
def get_death_date(soup, url):
    if soup.find(itemprop="deathDate") is not None:
        death_date = soup.find(itemprop="deathDate").text.split()
        del death_date[-1]
        death_date = death_date[0]
        death_date = death_date.split('.')
        day = death_date[0]
        month = death_date[1]
        year = death_date[2]
        date = year + month + day
        date = datetime.datetime.strptime(date, '%Y%m%d').date()
        return str(date)
    else:
        return ''


@logger
def get_height(soup, url):
    height = soup.find(itemprop="height").text
    height = height.replace(',', '.').replace('м', '')
    height = float(height) * 100
    return height


@logger
def get_nation_name(soup, url):
    nation_list = []
    container = soup.find(class_='info-table').find_all('span')
    boll = False
    for i in container:
        if boll:
            nation = i.find_all(class_='flaggenrahmen')
            for j in nation:
                nation_list.append(j.get('alt'))

        if i.text == 'Национальность:':
            boll = True
    return nation_list


@logger
def get_nation_id(nation, url):
    countries = json.load(open('C:\Football_transfer_bot\json\countries.json', 'r'))

    for country in countries:
        if country['name'] == nation:
            return country['id']
    return None


@logger
def get_position_name(soup, url):
    if soup.find(class_='detail-position__position') is not None:
        position_name = soup.find(class_='detail-position__position').text
    else:
        dataItems = soup.find_all(class_='dataItem')
        for dataItem in dataItems:
            if dataItem.text == 'Амплуа:':
                position_name = dataItem.find_next_sibling().text.strip()
    # store['positions'][position_id] = position_name
    return position_name


@logger
def get_national_team_name(soup, url):
    national_team = soup.find(class_='flaggenrahmen flagge').get('title')

    return national_team


@logger
def get_end_career_and_free_agent(soup, url):
    status = soup.find(class_='hauptpunkt').text.strip()
    if status == 'окончание':
        return True, False
    elif status == 'Без клуба':
        return False, True
    else:
        return False, False
        # store['players_info'][id]['end_career'] = False
        # store['players_info'][id]['free_agent'] = False


@logger
def get_rent_from(soup, url):
    # store['players_info'][id]['rent_from'] = ''
    rent = soup.find(class_='info-table').find_all('span')
    boll = False
    for i in rent:
        if boll:
            id = i.find('a').get('href')
            new_id = id.split('/')[-1]
            return new_id
            # store['players_info'][id]['rent_from'] = new_id
        if i.text == 'в аренде из:':
            boll = True


@logger
def get_price_and_currency(soup, url):
    price = soup.find(class_='right-td').text
    price = convert_price(price)
    return price
    # store['players_info'][id]['price'] = price[0]
    # store['players_info'][id]['currency'] = price[1]


@logger
def get_stadium_name(soup, url):
    dataItems = soup.find_all(class_='dataItem')
    for i in dataItems:
        if i.text == 'Стадион:':
            if i.find_next_sibling().find('a') is not None:
                stadium_name = i.find_next_sibling().find('a').text
                stadium_url = i.find_next_sibling().find('a').get('href')
                return stadium_name, stadium_url
            else:
                return '', ''


@logger
def get_stadium_id(stadium_name, url):
    stadiums_list = []
    file = open('stadiums_list.txt', 'r', encoding='utf-8')
    while True:
        line = file.readline()
        if line != '':
            stadiums_list.append(line.strip())
        if not line:
            break
    file.close()

    x = False
    for i in stadiums_list:
        if stadium_name == i:
            x = True
            index = stadiums_list.index(stadium_name)
            break
    if x:
        return index + 1
    else:
        stadiums_list.append(stadium_name)
        index = stadiums_list.index(stadium_name)
        file = open('stadiums_list.txt', 'a', encoding='utf-8')
        file.write(stadium_name)
        file.write('\n')
        file.close()
        return index + 1


@logger
def get_position_id(position_name, url):
    if not position_name: return -1

    positions_list = []
    file = open('positions_list.txt', 'r', encoding='utf-8')
    while True:
        line = file.readline()
        if line != '':
            positions_list.append(line.strip())
        if not line:
            break
    file.close()

    x = False
    for i in positions_list:
        if position_name == i:
            x = True
            index = positions_list.index(position_name)
            break
    if x:
        return index + 1
    else:
        positions_list.append(position_name)
        index = positions_list.index(position_name)
        file = open('positions_list.txt', 'a', encoding='utf-8')
        file.write(position_name)
        file.write('\n')
        file.close()
        return index + 1
