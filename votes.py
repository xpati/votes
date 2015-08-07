from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession

import RPi.GPIO as GPIO
import time


class VotesBackend(ApplicationSession):

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18,GPIO.OUT)
    GPIO.setup(23,GPIO.OUT)
    GPIO.setup(24,GPIO.OUT)

    GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)	   
    GPIO.setup(25,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.init()

    def init(self):
	self._votes = {
            'Banana': 0,
            'Chocolate': 0,
            'Lemon': 0,
	    'Winner':0	
        }

    @wamp.register(u'io.crossbar.demo.vote.get')
    def getVotes(self):
	print ("received request for current vote count = refresh")
        return [{'subject': key, 'votes': value} for key, value in self._votes.items()]

    @wamp.register(u'io.crossbar.demo.vote.vote')
    def submitVote(self, subject):
       	self._votes[subject] += 1
        result = {'subject': subject, 'votes': self._votes[subject]}
        self.publish('io.crossbar.demo.vote.onvote', result)
	print ("received vote for "+subject)
	if subject=="Banana":
		GPIO.output(24,GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(24,GPIO.LOW)
		print "banan"
	elif subject=="Chocolate":
		GPIO.output(23,GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(23,GPIO.LOW)
		print "choco"	
	elif subject=="Lemon":
		GPIO.output(18,GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(18,GPIO.LOW)
		print "lemon"
        return result

    @wamp.register(u'io.crossbar.demo.vote.reset')
    def resetVotes(self):
        self.init()
        self.publish('io.crossbar.demo.vote.onreset')
	print ("received vote reset")
	return "votes reset"

    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print("VotesBackend: {} procedures registered!".format(len(res)))
