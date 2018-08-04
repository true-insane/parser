#!/usr/bin/python3.6

import requests
import re
import csv
from bs4 import BeautifulSoup as Bs


def csv_writer(row):
    with open('exchange.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow((row['name'], row['url'],
                         row['date'], row['usd_buy'],
                         row['usd_sell'], row['eur_buy'],
                         row['eur_sell'], row['phone'],
                         row['adress'], row['time']))


def get_html(url):
    res = requests.get(url)
    if res.ok:
        return res.text
    print(res.status_code)


def get_data(html):
    soup = Bs(html, 'lxml')
    courses = soup.find('main', class_='layout-column-center')\
        .find_all('div', class_='calculator-hover-icon__container')
    result = []

    for course in courses:
        name = course.find('div', class_='table-flex__cell trades-table__name').find('a').text
        url = 'http://www.banki.ru' + course.find\
        ('div', class_='table-flex__cell trades-table__name').find('a').get('href')
        date_time = course.find('div', class_='font-size-small color-gray-gray').text.strip()
        currencies_rate = course.find_all('div', class_=re.compile('rate'))
        currency = []

        for currency_rate in currencies_rate:
            curr = currency_rate.text.strip()
            currency.append(curr)

        usd_buy = currency[0]
        usd_sell = currency[1]
        eur_buy = currency[2]
        eur_sell = currency[3]

        data = {'name': name, 'url': url, 'date': date_time, 'usd_buy': usd_buy, 'usd_sell': usd_sell,
                'eur_buy': eur_buy, 'eur_sell': eur_sell}
        result.append(data)
    return result


def get_info(data):
    for entry in data:
        url = entry['url']
        res = requests.get(url)
        soup = Bs(res.text, 'lxml')
        contacts = soup.find_all('div', class_='ui-columns ui-columns--colcount_2 ui-columns--responsive-collapse')[1]
        try:
            phones = contacts.find_all('span')[2].text
        except IndexError:
            phones = 'Нет данных'
        try:
            adress = contacts.find('div', class_='margin-bottom-x-small font-size-medium').find_all\
            ('div')[0].text.strip()
        except (IndexError, ValueError):
            adress = 'Адрес не указан'
        try:
            time = contacts.find('div', class_='exchange-schedule').find_all\
            ('div', class_='exchange-schedule__row')[0].find\
            ('div', class_='exchange-schedule__row__time').text.strip()[:11]
        except (IndexError, ValueError):
            time = 'Время работы не указано'

        new_data = {'phone': phones, 'adress': adress, 'time': time}

        entry.update(new_data)
        csv_writer(entry)


def main():
    url = 'http://www.banki.ru/products/currency/cash/moskva/'
    get_info(get_data(get_html(url)))


if __name__ == '__main__':
    main()
