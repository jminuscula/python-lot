import logging
from twython import Twython, TwythonStreamer


class LightOverTwitterStreamer(TwythonStreamer):

    def __init__(self, screen_name, auth, allowed, **kwargs):
        self.logger = logging.getLogger('lot.listener')
        self.logger.info('Logging with account "%s"' % screen_name)
        super(LightOverTwitterStreamer, self).__init__(*auth, **kwargs)

        self.screen_name = screen_name
        self.allowed_screen_names = allowed
        self.logger.info('Listening to stream…')

    def _is_allowed(self, data):
        if 'screen_name' in data.get('user', {}):
            sender = data['user']['screen_name']
            if sender not in self.allowed_screen_names:
                return False
        if 'user_mentions' in data.get('entities', {}):
            mentions = data['entities']['user_mentions']
            if self.screen_name not in (m['screen_name'] for m in mentions):
                return False
        return True

    def get_tags(self, data):
        if 'hashtags' in data.get('entities', {}):
            hashtags = (ht['text'] for ht in data['entities']['hashtags'])
            return [ht for ht in hashtags if ht in LightOverTwitterAction.tags]

    def on_success(self, data):
        text = data.get('text')
        if text is None:
            self.logger.debug("Received non text message")
            return

        if not self._is_allowed(data):
            self.logger.error("Received non qualifying message: %s" % text)
            return None

        tags = self.get_tags(data)
        if len(tags) > 0:
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
