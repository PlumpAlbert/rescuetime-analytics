#!/bin/env python3
from requests import get
from datetime import date
from os.path import expanduser
from sys import argv
from colorama import Fore, Back, Style
from platform import system
from os import linesep

sys_name = system()
if sys_name == "Windows":
    apikey = open(
        expanduser('~/.rescuetime'),
        'r'
    ).read().replace(linesep, '')
else:
    apikey = open(
        expanduser('~/.local/share/rescuetime.key'),
        'r'
    ).read().replace(linesep, '')


def productivity(number):
    if number == 2:
        return 'very productive'
    elif number == 1:
        return 'productive'
    elif number == 0:
        return 'neutral'
    elif number == -1:
        return 'distracting'
    else:
        return 'very distracting'


def get_data(from_date, to_date):
    url = 'https://www.rescuetime.com/anapi/data'
    params = {
        'key': apikey,
        'format': 'json',
        'perspective': 'interval',
        'resolution_time': 'day',
        'restrict_begin': str(from_date),
        'restrict_end': str(to_date),
        'restrict_kind': 'productivity'
    }
    data = get(url, params=params).json()
    headers = data['row_headers']
    for i, h in enumerate(headers):
        if 'Date' in h:
            date_index = i
        elif 'Productivity' in h:
            productivity_index = i
        elif 'Time' in h:
            time_index = i
    rows = data['rows']
    i = 0
    dict_data = {}
    for row in rows:
        key = row[date_index].split('T')[0]
        if key not in dict_data:
            dict_data[key] = {}
        hours = int(row[time_index] / 3600)
        minutes = int((row[time_index] % 3600) / 60)
        dict_data[key][productivity(
            row[productivity_index])] = f'{hours}:{minutes}'
    return dict_data


def get_time_by_productivity(day, type):
    time = [0, 0]
    p = productivity(type)
    if p in day:
        time = [int(t) for t in day[p].split(':')]
    return time


def print_table_header():
    columns = [
        Back.YELLOW + Fore.BLACK + 'Date'.center(12, ' '),
        Back.BLUE + Fore.BLACK + 'VP'.center(7, ' '),
        Back.CYAN + Fore.BLACK + 'P'.center(7, ' '),
        Back.WHITE + Fore.BLACK + 'N'.center(7, ' '),
        Back.MAGENTA + Fore.BLACK + 'D'.center(7, ' '),
        Back.RED + Fore.BLACK + 'VD'.center(7, ' ')
    ]
    print(''.join(columns) + Style.RESET_ALL)


if __name__ == '__main__':
    today = date.today()
    if "-l" in argv:
        from_date = date(today.year, today.month - 1, 1)
        to_date = date(today.year, today.month, 1)
    else:
        from_date = date(today.year, today.month, 1)
        to_date = today
    month = get_data(from_date, to_date)
    total_hours = total_minutes = 0
    print_table_header()
    for day in month:
        vp_time = get_time_by_productivity(month[day], 2)
        p_time = get_time_by_productivity(month[day], 1)
        n_time = get_time_by_productivity(month[day], 0)
        d_time = get_time_by_productivity(month[day], -1)
        vd_time = get_time_by_productivity(month[day], -2)
        h = int(vp_time[0]) + int(p_time[0])
        m = int(vp_time[1]) + int(p_time[1])
        if m > 60:
            h += int(m / 60)
            m %= 60
        total_hours += h
        total_minutes += m
        columns = [
            Fore.YELLOW + day + Style.RESET_ALL,
            f'{Fore.BLUE}{vp_time[0]:02d}:{vp_time[1]:02d}{Style.RESET_ALL}',
            f'{Fore.CYAN}{p_time[0]:02d}:{p_time[1]:02d}{Style.RESET_ALL}',
            f'{n_time[0]:02d}:{n_time[1]:02d}',
            f'{Fore.MAGENTA}{d_time[0]:02d}:{d_time[1]:02d}{Style.RESET_ALL}',
            f'{Fore.RED}{vd_time[0]:02d}:{vd_time[1]:02d}{Style.RESET_ALL}'
        ]
        for c in columns:
            print(' ' + c + ' ', end='')
        print()

    total_hours += int(total_minutes / 60)
    total_minutes = total_minutes % 60
    total_time = total_hours + float(f'{total_minutes / 60:.2f}')
    print(f'{Fore.GREEN}Total time:{Style.RESET_ALL} {total_hours}:{total_hours}')
    print(f'{Fore.GREEN}Total time (multiplied):{Style.RESET_ALL} {total_time * 1.33:.2f}')
    print(f'{Fore.GREEN}Money earned:{Style.RESET_ALL} {total_time * 1.33 * 200:.2f}')
