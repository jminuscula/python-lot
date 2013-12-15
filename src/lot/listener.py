"""
listener provides the functionality to listen to a twitter
stream and perform actions on the light based on the provided actions.
"""

import logging
import twython
import itertools
import time

from lot import light


class LightOverTwitterStreamer(twython.TwythonStreamer):

    logger = logging.getLogger('lot.listener')

    def __init__(self, screen_name, auth, allowed, **kwargs):
        self.logger.info('Logging in with account "%s"' % screen_name)
        super(LightOverTwitterStreamer, self).__init__(*auth, **kwargs)

        self.screen_name = screen_name
        self.allowed_screen_names = allowed
        self.logger.info('Listening to stream...')

    def _own_tweet(self, data):
        return data.get('user', {}).get('screen_name') == self.screen_name

    def _is_allowed(self, data):
        """
        Filters tweets not coming from allowed senders or not directed to user
        """
        sname = data.get('user', {}).get('screen_name')
        mentions = data.get('entities', {}).get('user_mentions')
        if sname and mentions:
            allowed = sname in self.allowed_screen_names
            mentioned = self.screen_name in (m['screen_name'] for m in mentions)
            return allowed and mentioned
        return False

    def get_tags(self, data):
        """
        Gets list of hashtags, which will be passed to the action
        """
        if 'hashtags' in data.get('entities', {}):
            hashtags = (ht['text'] for ht in data['entities']['hashtags'])
            return {ht for ht in hashtags if ht in LightOverTwitterAction.tags}

    def on_success(self, data):
        """
        Filters non-interesting tweets and processes the actions
        """
        text = data.get('text')
        if text is None:
            self.logger.debug("Received non text message")
            return

        if self._own_tweet(data):
            return

        if not self._is_allowed(data):
            self.logger.warning("Received non qualifying message: %s" % text)
            return

        tags = self.get_tags(data)
        if tags:
            self.logger.info("Processing message: %s" % text)
            return LightOverTwitterAction(tags)
        self.logger.warning("Received message without keywords: %s" % text)


class LightOverTwitterAction:

    actions = {'on', 'off', 'blink', 'reboot'}
    modifiers = {'force', 'long'}
    colors = getattr(light.LightController, 'COLORS', {})
    tags = set(itertools.chain(actions, modifiers, colors.keys()))

    light = light.LightController()

    def __init__(self, tags):
        self.logger = logging.getLogger('lot.listener')

        action = None
        modifiers = set()
        color = None

        for tag in tags:
            if tag in self.actions:
                action = getattr(self, tag, None)
            elif tag in self.modifiers:
                modifiers.add(tag)
            elif tag in self.colors:
                color = tag

        if action:
            action(modifiers=modifiers, color=color)
        else:
            self.logger.error('Message had no actions')

    def on(self, modifiers=None, color=None):
        self.logger.info("ON")
        if color is not None:
            self.light.change_color(color)
        else:
            self.light.turn_on()

    def off(self, *args, **kwargs):
        self.logger.info("OFF")
        self.light.turn_off()

    def blink(self, *args, **kwargs):
        self.logger.info("BLINK")
        repeat, on_ms, off_ms = 10, 0.5, 0.5
        for i in range(repeat):
            self.light.switch()
            time.sleep(on_ms)
            self.light.switch()
            time.sleep(off_ms)

    def reboot(self, *args, **kwargs):
        self.light.turn_off()
        self.logger.info('Rebooting system')
        import os
        os.system('reboot')


def listen(user, auth, allowed):
    stream = LightOverTwitterStreamer(user, auth, allowed)
    return stream.user()
