import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from random import choice
from re import match
from time import sleep
from optparse import OptionParser

class ChatBuddy(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        self.register_plugin('xep_0085') # Chat States
        self.add_event_handler("chatstate_composing", self.composing)
        self.add_event_handler("chatstate_active", self.active)
        self.add_event_handler("chatstate_paused", self.paused)
        self.add_event_handler("chatstate_inactive", self.inactive)
        self.add_event_handler("chatstate_gone", self.gone)

        self._wait_for_client = False

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

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def is_greeting(self, message):
        greetings = ["hi", "Hi", "hello", "Hello", "hey", "Hey"]
        for greeting in greetings:
            if match(r"\b%s\b"%(greeting), message):
                return True

    def pick_response(self, message):
        if self.is_greeting(message):
            response = choice(self._greetings)
            self._message_count = 0
        else:
            if self._message_count % 5 == 0:
                response = choice(self._actions)
            else:
                response = choice(self._responses)
        print "picking %s" % response
        return response

    def send_reply(self, msg, message):
        self._last_response = message
        self._message_count += 1
        sleep(1)
        msg.reply(message).send()
        self._cached_response = ""

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
            if self._wait_for_client:
                self._cached_response = response
            else:
                self.send_reply(msg, response)

    def composing(self, msg):
        self._wait_for_client = True

    def active(self, msg):
        self._wait_for_client = False
        self.send_reply(msg, self._cached_response)

    def paused(self, msg):
        self._wait_for_client = False
        self.send_reply(msg, self._cached_response)

    def gone(self, msg):
        self._wait_for_client = False
        self.send_reply(msg, self._cached_response)

    def inactive(self, msg):
        self._wait_for_client = False
        self.send_reply(msg, self._cached_response)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username",
                      help="username for ChatBuddy account") 
    parser.add_option("-p", "--password", dest="password",
                      help="password for ChatBuddy account")
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = ChatBuddy(options.username, options.password)
    xmpp.connect()
    xmpp.process(block=True)
