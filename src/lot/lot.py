#!/usr/bin/env python3

import sys
import os.path
import logging

import json
from functools import wraps
from multiprocessing import Process

from listener import listen


def quiet(fn):
    @wraps(fn)
    def no_keyboard_interrupt(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyboardInterrupt:
            sys.exit(-1)
    return no_keyboard_interrupt


@quiet
def listener(config):
    logger = logging.getLogger('lot.listener')
    screen_name = config['screen_name']
    auth = (config['auth']['app_key'], config['auth']['app_secret'],
            config['auth']['oauth_token'], config['auth']['oauth_token_secret'])
    allowed = config['listener']['allowed']
    listen(screen_name, auth, allowed)


@quiet
def publisher(config):
    logger = logging.getLogger('lot.publisher')
    logger.error('No action defined for publisher')


def setup():
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)

    paths = ('settings.json',
             '../settings.json',
             '~/.lot.json',
             '~/.config/lot.json',
             '~/.lot/settings.json')

    for path in paths:
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
