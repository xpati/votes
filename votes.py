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
	GPIO.add_event_detect(17,GPIO.FALLING,callback=self.my_callback, bouncetime=500)
	GPIO.add_event_detect(22,GPIO.FALLING,callback=self.my_callback,bouncetime=500)
	GPIO.add_event_detect(25,GPIO.FALLING,callback=self.my_callback,bouncetime=500)

    def init(self):
	self._votes = {
            'Banana': 0,
            'Chocolate': 0,
            'Lemon': 0,
	    'Winner':0	
        }

  
    def turnsON(self,subject):
	if subject == "Banana":
		number=24
	elif subject == "Chocolate":
		number = 23
	elif subject == "Lemon":
		number = 18
	GPIO.output(number,GPIO.HIGH)
	time.sleep(0.1)
	GPIO.output(number,GPIO.LOW)

    def my_callback(self,number):
	print number
	if number == 17:
		self.submitVote("Lemon")
	if number == 22:
		self.submitVote("Chocolate")
	if number==25:
		self.submitVote("Banana")


   #   GPIO.add_event_detect(22,GPIO.RISING,callback=my_callback)
   # GPIO.add_event_detect(25,GPIO.RISING,callback=my_callback) 	
   
    @wamp.register(u'io.crossbar.demo.vote.get')
    def getVotes(self):
	print ("received request for current vote count = refresh")
#	self.my_callback(17)
        return [{'subject': key, 'votes': value} for key, value in self._votes.items()]

    @wamp.register(u'io.crossbar.demo.vote.vote')
    def submitVote(self, subject):
       	self._votes[subject] += 1
        result = {'subject': subject, 'votes': self._votes[subject]}
        self.publish('io.crossbar.demo.vote.onvote', result)
	print ("received vote for "+subject)
	self.turnsON(subject)
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
