#!/usr/local/bin/python
"""
Main
"""

import os
import json
import time
import logging
from string import whitespace

from exchange import ExchangeAggregator
from notification import Notifier
from analysis import StrategyAnalyzer


# Let's test an API call to get our BTC balance as a test
# print(BITTREX_CLIENT.get_balance('BTC')['result']['Balance'])

#print(historical_data = BITTREX_CLIENT.get_historical_data('BTC-ETH', 30, "thirtyMin"))

def get_signal():
    
    for coin_pair in COIN_PAIRS:
        breakout_value, is_breaking_out = STRATEGY_ANALYZER.analyze_breakout(
            EXCHANGE_AGGREGATOR.get_historical_data(coin_pair))
        if is_breaking_out:
            NOTIFIER.notify_all(message="{} is breaking out!".format(coin_pair))
        print("{}: \tBreakout: {}".format(coin_pair, breakout_value))
    time.sleep(300)

if __name__ == "__main__":
    # Load settings and create the CONFIG object
    SECRETS = {}
    if os.path.isfile('secrets.json'):
        SECRETS = json.load(open('secrets.json'))
    CONFIG = json.load(open('default-config.json'))

    CONFIG.update(SECRETS)

    CONFIG['settings']['market_pairs'] = os.environ.get('MARKET_PAIRS', CONFIG['settings']['market_pairs'])
    CONFIG['settings']['loglevel'] = os.environ.get('LOGLEVEL', logging.INFO)
    CONFIG['exchanges']['bittrex']['required']['key'] = os.environ.get('BITTREX_KEY', CONFIG['exchanges']['bittrex']['required']['key'])
    CONFIG['exchanges']['bittrex']['required']['secret'] = os.environ.get('BITTREX_SECRET', CONFIG['exchanges']['bittrex']['required']['secret'])
    CONFIG['notifiers']['twilio']['required']['key'] = os.environ.get('TWILIO_KEY', CONFIG['notifiers']['twilio']['required']['key'])
    CONFIG['notifiers']['twilio']['required']['secret'] = os.environ.get('TWILIO_SECRET', CONFIG['notifiers']['twilio']['required']['secret'])
    CONFIG['notifiers']['twilio']['required']['sender_number'] = os.environ.get('TWILIO_SENDER_NUMBER', CONFIG['notifiers']['twilio']['required']['sender_number'])
    CONFIG['notifiers']['twilio']['required']['receiver_number'] = os.environ.get('TWILIO_RECEIVER_NUMBER', CONFIG['notifiers']['twilio']['required']['receiver_number'])

    # Set up logger
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(CONFIG['settings']['loglevel'])

    LOG_FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_HANDLE = logging.StreamHandler()
    LOG_HANDLE.setLevel(logging.DEBUG)
    LOG_HANDLE.setFormatter(LOG_FORMAT)
    LOGGER.addHandler(LOG_HANDLE)

    EXCHANGE_AGGREGATOR = ExchangeAggregator(CONFIG)
    STRATEGY_ANALYZER = StrategyAnalyzer()
    NOTIFIER = Notifier(CONFIG)

    # The coin pairs
    COIN_PAIRS = []
    if CONFIG['settings']['market_pairs']:
        COIN_PAIRS = CONFIG['settings']['market_pairs'].translate(str.maketrans('', '', whitespace)).split(",")
    else:
        user_markets = EXCHANGE_AGGREGATOR.get_user_markets()
        for user_market in user_markets['result']:
            if 'BTC' in user_market['Currency']:
                continue
            market_pair = 'BTC-' + user_market['Currency']
            COIN_PAIRS.append(market_pair)
    LOGGER.debug(COIN_PAIRS)

    while True:
        get_signal()
