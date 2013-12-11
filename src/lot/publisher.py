"""
publisher provides the functionality to monitor the Rpi GPIO pins and
detect push button events, sending synchronization messages over Twitter.
"""

import time
import logging
import twython
import traceback

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import Mock
    GPIO = Mock()
from lot import light


class LightOverTwitterAnnouncer:

    def __init__(self, config):
        self.logger = logging.getLogger('lot.publisher')

        self.screen_name = config['screen_name']
        self.pair_screen_name = config['pair_screen_name']

        self.logger.info('Connecting publisher to twitter account "%s"' % self.screen_name)
        self.twitter = twython.Twython(*config['auth'])

        # sync initial status
        self.publish("I'm alive!")

    def publish(self, text):
        ts = int(time.time())
        text = "{0} {1}".format(text, ts)
        try:
            self.logger.debug('Publishing "%s"' % text)
            return self.twitter.update_status(status=text)
        except twython.exceptions.TwythonError:
            self.logger.error(traceback.format_exc())
            return False

    def publish_state(self, tags):
        text = ' '.join('#%s' % t for t in tags)
        text = "@{0} {1}".format(self.pair_screen_name, text)
        return self.publish(text)

    def publish_on(self):
        self.logger.info('Announcing ON state')
        return self.publish_state(["on"])

    def publish_off(self):
        self.logger.info('Announcing OFF state')
        return self.publish_state(["off"])


class LightOverTwitterSwitch:

    def __init__(self, conf, announcer):
        self.logger = logging.getLogger('lot.publisher')

        self.on = False
        self.switch_channel = conf.get('switch_channel', 3)
        self.bouncetime = conf.get('bouncetime', 300)
        self.wait = conf.get('wait', 1000)
        self.setup_gpio()

        # twitter interface instance
        self.announcer = announcer

        # physical light controller
        self.light = light.LedborgController()

        # sync initial status
        self.turn_off()

        # bind the channel interrupt to the event
        self.logger.info('Listening to switch interruptions')
        GPIO.add_event_detect(self.switch_channel, GPIO.FALLING,
                              self.pressed, bouncetime=self.bouncetime)

        # check for events only at wait intervals
        while True:
            time.sleep(self.wait)

    def setup_gpio(self):
        GPIO.cleanup()
        # set the GPIO to use Board channel numbering
        GPIO.setmode(GPIO.BOARD)
        # set the switch channel as an input pin
        GPIO.setup(self.switch_channel, GPIO.IN, initial=GPIO.HIGH)

    def pressed(self, channel):
        self.logger.debug('Button pressed!')
        action = self.turn_off if self.on else self.turn_on
        self.on = action()

    def turn_on(self):
        self.logger.info('Turning on')
        on = self.light.turn_on()
        if on:
            return self.announcer.publish_on()
        return self.on

    def turn_off(self):
        self.logger.info('Turning off')
        off = self.light.turn_off()
        if off:
            return not self.announcer.publish_off()
        return self.on


def publish(twitter_conf, light_conf):
    announcer = LightOverTwitterAnnouncer(twitter_conf)
    switch = LightOverTwitterSwitch(light_conf, announcer)
