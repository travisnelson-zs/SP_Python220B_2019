""""
Returns total price paid for individual rentals
"""
import argparse
import json
import datetime
import math
import logging
import sys

#format for the log
LOG_FORMAT = "%(asctime)s %(filename)s: %(lineno)-3d %(levelname)s %(message)s"

#setup for formatter and log file
FORMATTER = logging.Formatter(LOG_FORMAT)
LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d")+'.log'

#setup for file hanlder at error level
FILE_HANDLER = logging.FileHandler(LOG_FILE, mode='w')
FILE_HANDLER.setLevel(30)
FILE_HANDLER.setFormatter(FORMATTER)

#setup for console handler at debug level
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(10)
CONSOLE_HANDLER.setFormatter(FORMATTER)

#setup for logging set at debug level
LOGGER = logging.getLogger()
LOGGER.setLevel(10)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(CONSOLE_HANDLER)

#dict to convert debug input to log level
LOG_LEVEL = {'0': 51, '1': 40, '2': 30, '3': 10}


def parse_cmd_arguments():
    """
    Parse the input, ouptut, and debug arguments into interpreted text
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input', help='input JSON file', required=True)
    parser.add_argument('-o', '--output', help='ouput JSON file', required=True)
    #adding debug argument for parsing
    parser.add_argument('-d', '--debug', help='debug level',
                        default='0', choices=('0', '1', '2', '3'))

    return parser.parse_args()


def load_rentals_file(filename):
    """
    Load the rentals file
    """
    with open(filename) as file:
        #setting up message to see which file is opened
        logging.debug('Attempting to open file %s', filename)
        try:
            data = json.load(file)
            #to show file open succesfully
            logging.debug('File loaded successfully!')
        except FileNotFoundError:
            #to show file didn't open
            logging.error('Unable to load file')
            sys.exit()
    return data

def calculate_additional_fields(data):
    """
    Calculates data based on inputted data for a certain rental ID
    """
    #adjusted to key, value in order to debug keys
    for key, value in data.items():
        try:

            rental_start = datetime.datetime.strptime(value['rental_start'], '%m/%d/%y')
            #show rental start
            logging.debug('Rental start: %s', rental_start)
            #adding warning for blank rental end
            try:
                rental_end = datetime.datetime.strptime(value['rental_end'], '%m/%d/%y')
            except ValueError:
                logging.warning('Rental end for %s is not defined', key)
                continue

            #show rental end
            logging.debug('Rental end: %s', rental_end)
            value['total_days'] = (rental_end - rental_start).days
            #show total days
            logging.debug('Total days for %s: %s', key, value['total_days'])

            #cannot have a negative number of days
            if value['total_days'] < 0:
                logging.error('Number of days for %s are negative', key)

            value['total_price'] = value['total_days'] * value['price_per_day']
            #show total price
            logging.debug('Total price for %s: %s', key, value['total_price'])

            #cannot take square root of a negative
            try:
                value['sqrt_total_price'] = math.sqrt(value['total_price'])
            except ValueError:
                logging.error('Cannot divide by negative number: %s', value['total_price'])

            logging.debug('United rented for %s: %s', key, value['units_rented'])
            #cannot divide by zero
            try:
                value['unit_cost'] = value['total_price'] / value['units_rented']
            except ZeroDivisionError:
                logging.error('Cannot divide %s by %s', value['total_price'], value['units_rented'])

        except ValueError:
            #to show at what item error occured
            logging.debug('Faulted item: %s', key)
            sys.exit()

    return data

def save_to_json(filename, data):
    """
    Saves outputted file
    """
    with open(filename, 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    ARGS = parse_cmd_arguments()
    #set default level based on debug input
    LOGGER.setLevel(LOG_LEVEL[ARGS.debug])
    #show input, output, and logging files
    logging.debug('Input file: %s \nOutput file: %s \nLogging file: %s',
                  ARGS.input, ARGS.output, LOG_FILE)
    DATA = load_rentals_file(ARGS.input)
    DATA = calculate_additional_fields(DATA)
    save_to_json(ARGS.output, DATA)
