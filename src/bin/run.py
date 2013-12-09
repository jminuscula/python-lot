#!/usr/bin/env python3

import sys
import os.path
import logging

import json
from functools import wraps
from multiprocessing import Process

from lot.listener import listen
from lot.publisher import publish


def quiet(fn):
    @wraps(fn)
    def no_keyboard_interrupt(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyboardInterrupt:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            sys.exit(-1)
    return no_keyboard_interrupt


def twitter_config(config):
    return {
        'screen_name': config['screen_name'],
        'pair_screen_name': config['pair_screen_name'],
        'allowed': config['listener']['allowed'],
        'auth': (config['auth']['app_key'], config['auth']['app_secret'],
                 config['auth']['oauth_token'], config['auth']['oauth_token_secret']),
    }

@quiet
def listener(config):
    logger = logging.getLogger('lot.listener')
    conf = twitter_config(config)
    listen(conf['screen_name'], conf['auth'], conf['allowed'])


@quiet
def publisher(config):
    logger = logging.getLogger('lot.publisher')
    conf = twitter_config(config)
    publish(conf)


def setup():
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)

    paths = ('settings.json',
             'config/settings.json',
             '../settings.json',
             '../config/settings.json',
             '~/.lot.json',
             '~/.config/lot.json',
             '~/.lot/settings.json')

    for path in map(os.path.realpath, paths):
        if os.path.isfile(path):
            with open(path, 'r') as settings:
                return json.load(settings)

@quiet
def run():
    config = setup()
    tasks = [Process(target=task, args=(config, )) for task in (listener, publisher)]

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


if __name__ == '__main__':
    run()
