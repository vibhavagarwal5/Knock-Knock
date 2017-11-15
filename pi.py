from subprocess import call
import RPi.GPIO as GPIO
from time import time, sleep
import datetime
from twilio.rest import Client






snap_dir = "./snaps/"
MAX_TRIGGER_DISTANCE = 150   
MIN_TRIGGER_DISTANCE = 30    
VALID_PIC_THRESHOLD = 5     # weak attempt at mitigating "noise" (butterfly/moth/squirrel)
account_sid = "AC87fbb7affe55b87c4e2a8cf3a64abe26"
auth_token = "574245ac21cf74a3d183f444a0bd9607"
client = Client(account_sid, auth_token)

while True :
    GPIO.setmode(GPIO.BCM)

    TRIG = 23
    ECHO = 24

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

    if distance<MAX_TRIGGER_DISTANCE and distance>MIN_TRIGGER_DISTANCE:
        now = datetime.datetime.now()
    	snap_filename = "visitor-%d:%d:%d-%d:%d:%d.jpg" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        take_snap_cmd = "fswebcam -d /dev/video0 "+ snap_dir + snap_filename

        print "\n\n************************** Taking a Snapshot  ************************ \n\n"

        snap_return_code = call(take_snap_cmd, shell=True)
        print "Snapshot return code is ", snap_return_code

	close_cam_cmd="sudo fswebcam -b"
	call_close_cmd=call(close_cam_cmd,shell=True)

        print "\n\n************************** Uploading on Git ***********************\n\n"

        git_upload = "git add ." + \
                  "; git commit -m \"another visitor\" " + snap_dir + \
                  "; git push"
        git_return_code = call(git_upload, shell=True)
        print "Git stuff return code is ", git_return_code

        print "\n\n****************************  Sending SMS  **********************\n\n"

        message = client.messages.create(
                            to="+919810778985",
                            #check this no if not working..
                            from_="+13213513859",
                            body="Hey, you have a visitor at the front door: " +
                            "https://raw.githubusercontent.com/vibhavagarwal5/Knock-Knock/master/snaps/"+snap_filename
                        )
        print "\n\n****************************  SMS Sent  **********************\n\n"
    sleep(15)
    
