import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from random import choice
from re import match

class ChatBuddy(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

	self._last_response = ""
	self._message_count = 0

	self._greetings = [\
	    "Hey, how are you?",
	    "Hi, how are you today?",
	    "What's happening?",
	    "Hello, how are you feeling?",
	    "Nice to see you online! How has your day been?",
	    "Hi, what's going on?"
	]
	self._responses = [\
	    "hmm, tell me more",
	    "uh huh",
	    "yeah?",
	    "tell me more about that",
	    "how does that make you feel?"
	]
	self._actions = [\
	    "what do you think could make you feel better?",
	    "what could you do now?",
	    "what are your plans for tomorrow?",
	    "are you feeling any better?",
	    "would getting some fresh air help clear your head?",
	    "is there anything you could do about this?"
	]

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def is_greeting(self, message):
	greetings = ["hi", "Hi", "hello", "Hello"]
	for greeting in greetings:
	    if match(r"\b%s\b"%(greeting), message):
		return True

    def pick_response(self, message):
	if self.is_greeting(message):
	    response = choice(self._greetings)
	else:
	    if self._message_count > 0 and self._message_count % 5 == 0:
		response = choice(self._actions)
	    else:
		response = choice(self._responses)
	print "picking %s" % response
	return response

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
	    response = ""
	    if "feel" in msg['body']:
		response = "why do you feel that way?"
	    else:
		print "last response: %s" % self._last_response
		while True:
		    print "response = %s" % response
		    response = self.pick_response(msg['body'])
		    if response != self._last_response:
			break
	    self._last_response = response
	    self._message_count += 1
            msg.reply(response).send()


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = ChatBuddy('chatbuddy@jabber.org', 'chatbuddy')
    xmpp.connect()
    xmpp.process(block=True)
