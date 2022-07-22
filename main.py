import argparse
from string import Template
from os import path, linesep, environ
from platform import system
from rescuetime import analytic_data
from datetime import date
from colorama import Fore, Back, Style
from csv import DictReader
from json import load
import math

parser = argparse.ArgumentParser(
    description='RescueTime Analytic API from your command line')
# PARSE ARGUMENTS
parser.add_argument('-k', '--key', dest='k', metavar='KEY', type=str,
                    help="RescueTime API key for the user")
parser.add_argument('-f', '--file', dest='file', metavar='FILE', type=str,
                    help="Path to the file with user's API key")
parser.add_argument('--start', nargs=1, dest='rb', metavar='YYYY-MM-DD', type=str,
                    help="Sets the start day for data batch, inclusive.\
                    (always at time 00:00, start hour/minute not supported)")
parser.add_argument('--end', nargs=1, dest='re', metavar='YYYY-MM-DD', type=str,
                    help="Sets the end day for data batch, inclusive.\
                    (always at time 00:00, start hour/minute not supported)")
parser.add_argument('-w', '--wage', dest='wage', type=float,
                    help="Amount of money you earn per productive hour")
parser.add_argument('--multiplier', type=float,
                    help="If provided all productive time will be multiplied by that value")
###
args = dict(parser.parse_args()._get_kwargs())
if args['k']:
    apikey = args['k']
elif args['file']:
    if not path.exists(args['k']):
        raise FileNotFoundError("\"%s\" : File does not exists" % (args['k']))
    apikey = open(args['k'], 'r').read().replace(linesep, '')
else:
    rescuetime_config_file = None
    if system() == "Linux":
        rescuetime_config_file = open(
            path.expanduser('~/.config/RescueTime.com/rescuetimed.json'),
            'r'
        )
    elif system() == 'Windows':
        rescuetime_config_file = open(
            Template('$LOCALAPPDATA/RescueTime.com/rescuetimed.json').substitute(environ),
            'r'
        )
    if rescuetime_config_file:
        config = load(rescuetime_config_file)
        apikey = config['data_key']

if not apikey:
    raise Exception("No API key provided")

today = date.today()
start_of_the_month = date(today.year, today.month, 1)

data = analytic_data(apikey, **{
    'pv': 'interval',
    'rs': 'day',
    'rb': str(args['rb'] or start_of_the_month),
    're': str(args['re'] or today),
    'rk': 'productivity',
    'format': 'csv'
})

r = DictReader(data.splitlines())
day_info = {}
for row in r:
    label = row['Date'].split('T')[0]
    if label not in day_info:
        day_info[label] = {}
    _prop = ''
    if int(row['Productivity']) == 2:
        _prop = 'VP'
    elif int(row['Productivity']) == 1:
        _prop = 'P'
    elif int(row['Productivity']) == 0:
        _prop = 'N'
    elif int(row['Productivity']) == -1:
        _prop = 'D'
    elif int(row['Productivity']) == -2:
        _prop = 'VD'
    day_info[label][_prop] = int(row['Time Spent (seconds)'])
# Fill empty productivity categories with 0
for day in day_info:
    for p in ['VP', 'P', 'N', 'D', 'VD']:
        if p not in day_info[day]:
            day_info[day][p] = 0


def print_day(day, **kwargs):
    text = day.center(10, ' ')
    print(Fore.GREEN + text + Style.RESET_ALL, end='')
    for key in ['VP', 'P', 'N', 'D', 'VD']:
        if key == 'VP':
            fc = Fore.BLUE
        elif key == 'P':
            fc = Fore.CYAN
        elif key == 'N':
            fc = Fore.WHITE
        elif key == 'D':
            fc = Fore.YELLOW
        else:
            fc = Fore.RED
        s = kwargs[key] or 0
        m, s = divmod(int(s), 60)
        h, m = divmod(m, 60)
        text = f'{h:02d}:{m:02d}'.center(7, ' ')
        print(fc + text + Style.RESET_ALL, end='')
    print()


def print_table_header():
    columns = [
        Back.GREEN + Fore.BLACK + 'Date'.center(10, ' '),
        Back.BLUE + Fore.BLACK + ' VP'.center(7, ' '),
        Back.CYAN + Fore.BLACK + 'P'.center(7, ' '),
        Back.WHITE + Fore.BLACK + 'N'.center(7, ' '),
        Back.YELLOW + Fore.BLACK + 'D'.center(7, ' '),
        Back.RED + Fore.BLACK + 'VD'.center(7, ' ')
    ]
    print(''.join(columns) + Style.RESET_ALL)


print_table_header()
for day in day_info:
    print_day(day, **day_info[day])

productive_time = 0
for day in day_info:
    current_day = day_info[day]
    if 'VP' in current_day:
        productive_time += int(current_day['VP'])
    if 'P' in current_day:
        productive_time += int(current_day['P'])
if args['multiplier']:
    productive_time = math.floor(productive_time * args['multiplier'])
m, s = divmod(productive_time, 60)
h, m = divmod(m, 60)
print(
    f'Total productive hours: {Fore.GREEN}{math.floor(h)}h {m}min {s}sec{Style.RESET_ALL}')
if args['wage']:
    print(f'Your wage is {Fore.GREEN}{(h + m/60) * args["wage"]:.2f}{Style.RESET_ALL}')
