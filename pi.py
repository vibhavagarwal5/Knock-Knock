from subprocess import call
import RPi.GPIO as GPIO
from time import time, sleep
import datetime

import urllib2
import cookielib
from getpass import getpass
import sys
import os
from stat import *


snap_dir = "./snaps/"
MAX_TRIGGER_DISTANCE = 150
MIN_TRIGGER_DISTANCE = 30
VALID_PIC_THRESHOLD = 5     # weak attempt at mitigating "noise"

#Way2Sms login details
username = ""
passwd = ""
number=""

while True :
    GPIO.setmode(GPIO.BCM)

    TRIG = 23   #trigger pin of HC-SR04 connected to Pin number 23
    ECHO = 24   #echo pin of HC-SR04 connected to Pin number 24

    print "Distance Measurement In Progress"
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, False)
    print "Waiting For Sensor To Settle"
    sleep(3)

    GPIO.output(TRIG, True)
    sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
      pulse_start = time()

    while GPIO.input(ECHO)==1:
      pulse_end = time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    distance = round(distance, 2)

    print "Distance:",distance,"cm"

    GPIO.cleanup()

#-------------------------Using the Ultrasonic sensor to measure the distance--------------------------------------

    if distance<MAX_TRIGGER_DISTANCE and distance>MIN_TRIGGER_DISTANCE:
        now = datetime.datetime.now()
    	snap_filename = "visitor-%d:%d:%d-%d:%d:%d.jpg" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        take_snap_cmd = "fswebcam -d /dev/video0 "+ snap_dir + snap_filename
        print "\n\n************************** Taking a Snapshot  ************************ \n\n"

        snap_return_code = call(take_snap_cmd, shell=True)
        print "Snapshot return code is ", snap_return_code

        print "\n\n************************** Uploading on Git ***********************\n\n"

        git_upload = "git add ." + \
                  "; git commit -m \"another visitor\" " + snap_dir + \
                  "; git push"
        git_return_code = call(git_upload, shell=True)
        print "Git stuff return code is ", git_return_code

        print "\n\n****************************  Sending SMS  **********************\n\n"

#-----------------------------WAY2SMS implementation code------------------------------------------

	message="Hey, You have a visitor at your front door "+"https://github.com/vibhavagarwal5/Knock-Knock/tree/master/snaps/"+snap_filename
   	message = "+".join(message.split(' '))

        url ='http://site24.way2sms.com/Login1.action?'
        data = 'username='+username+'&password='+passwd+'&Submit=Sign+in'

        cj= cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	opener.addheaders=[('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120')]
	try:
		usock =opener.open(url, data)
	except IOError:
		print "error"

	jession_id =str(cj).split('~')[1].split(' ')[0]
	send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
	send_sms_data = 'ssaction=ss&Token='+jession_id+'&mobile='+number+'&message='+message+'&msgLen=136'
	opener.addheaders=[('Referer', 'http://site25.way2sms.com/sendSMS?Token='+jession_id)]
	try:
		sms_sent_page = opener.open(send_sms_url,send_sms_data)
	except IOError:
		print "error"

    	print "success"
        print "\n\n****************************  SMS Sent  **********************\n\n"
    sleep(12)
    #close_cam_cmd="sudo fswebcam -b"
    #call_close_cmd=call(close_cam_cmd,shell=True)
