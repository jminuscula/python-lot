"""
listener provides the functionality to listen to a twitter
stream and perform actions on the light based on the provided actions.
"""

import logging
import twython


class LightOverTwitterStreamer(twython.TwythonStreamer):

    logger = logging.getLogger('lot.listener')

    def __init__(self, screen_name, auth, allowed, **kwargs):
        self.logger.info('Logging in with account "%s"' % screen_name)
        super(LightOverTwitterStreamer, self).__init__(*auth, **kwargs)

        self.screen_name = screen_name
        self.allowed_screen_names = allowed
        self.logger.info('Listening to stream...')

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
            return [ht for ht in hashtags if ht in LightOverTwitterAction.tags]

    def on_success(self, data):
        """
        Filters non-interesting tweets and processes the actions
        """
        text = data.get('text')
        if text is None:
            self.logger.debug("Received non text message")
            return

        if not self._is_allowed(data):
            self.logger.warning("Received non qualifying message: %s" % text)
            return

        tags = self.get_tags(data)
        if tags:
            self.logger.info("Processing message: %s" % text)
            return LightOverTwitterAction(tags)
        self.logger.warning("Received message without action: %s" % text)


class LightOverTwitterAction:

    actions = ['on', 'off']
    tags = actions

    def __init__(self, tags):
        self.logger = logging.getLogger('lot.listener')

        if len(tags) != 1:
            self.logger.error("Ambiguous action. Aborted.")
            return

        return getattr(self, tags[0])()

    def on(self):
        self.logger.info("ON")

    def off(self):
        self.logger.info("OFF")

    def color(self):
        pass


def listen(user, auth, allowed):
    stream = LightOverTwitterStreamer(user, auth, allowed)
    return stream.user()
