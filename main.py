# main import for matlab engine
import matlab.engine as mat
# imports related to audio record
import pyaudio
import wave
# imports related to SMS send
import urllib
import requests
#imports related to server discovery
from socket import socket, AF_INET, SOCK_DGRAM
# imports related to Video Capture
from VideoCapture import Device
import numpy as np
import cv2
# imports related to FPS calculation
import time
## imports related to email sending
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

from config import *

from recognise import findPerson

from time import strftime
from multiprocessing import Process

#######################################################################################
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
PHONE_NUMBER = ""  
SMS_GATEWAY_IP = ""
SMS_GATEWAY_PORT = ""
VIDEO_OUTPUT_FILENAME = "output.avi"
FROM_EMAIL = ""
TO_EMAIL = ""
EMAIL_PASS = ""
#######################################################################################

def setGatewayIP():
    """
    Getting IP addr from announcement from server script
    """
    global SMS_GATEWAY_IP
    PORT = 50000
    MAGIC = "fna349fn" #to make sure we don't confuse or get confused by other programs

    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', PORT))

    i=0
    while 1:
        data, addr = s.recvfrom(1024) #wait for a packet
        if data.startswith(MAGIC):
            print "Found SMS Gateway at IP: ", addr[0]
            SMS_GATEWAY_IP = addr[0]
            break
        i = i+1
        if i == 10:
            print "SMS Gateway was not found about 10 tries, quitting"
            exit(1)
def sendSMS(knocks,person):
    """
    Building URL with given params, sending get requests to gateway IP
    """
    msg = "I found %d knocks!" % knocks
    print msg
    message = msg+" "+person+" was near your door, Please enter your Gmail to see, you can call him at: "+People[person]
    data = {
      'smsto': PHONE_NUMBER,
      'smsbody': message,
      'smstype': 'sms'
    }
    params = urllib.urlencode(data)
    url = "http://"+SMS_GATEWAY_IP+":"+SMS_GATEWAY_PORT+"/send.html"

    r = requests.get(url, params=params)
    if r.status_code == 200:
      print "SMS SENT"
def recordSound():
    """
    Starting audio device, recoding RECORD_SECONDS of sound, and saves the file on directory
    """
    # start audio object
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print "recording %d seconds..." % RECORD_SECONDS

    frames = []

    # start Recording
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"

    # stop record and close object
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save file
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
def getSnapShot():
    cam = Device()
    cam.saveSnapshot("image.jpg", timestamp=3, boldfont=1)
def showMyFace():
    getSnapShot()
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    img = cv2.imread('image.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def getFPS():
    # Start default camera
    video = cv2.VideoCapture(0);

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    # With webcam get(CV_CAP_PROP_FPS) does not work.
    # Let's see for ourselves.

    if int(major_ver)  < 3 :
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps)
    else :
        fps = video.get(cv2.CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)

    # Number of frames to capture
    num_frames = 120;

    print "Capturing {0} frames".format(num_frames)

    # Start time
    start = time.time()

    # Grab a few frames
    for i in xrange(0, num_frames) :
        ret, frame = video.read()

    # End time
    end = time.time()

    # Time elapsed
    seconds = end - start
    print "Time taken : {0} seconds".format(seconds)

    # Calculate frames per second
    fps  = num_frames / seconds;
    print "Estimated frames per second : {0}".format(fps);

    # Release video
    video.release()
def getVideo():
    formatted_Time = float(50*60.0/3600.0)
    print "Recording video for %.3f seconds" % formatted_Time
    cap = cv2.VideoCapture(0)
    # fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    ############################################# TODO fix!!
    fourcc = cv2.cv.CV_FOURCC('X', '2', '6', '4')
    #############################################
    out = cv2.VideoWriter(VIDEO_OUTPUT_FILENAME, fourcc, 15.0, (640,480))
    i=0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            out.write(frame)
            if (i*60.0/3600.0) == formatted_Time:
                break
        else:
            print "Could not read capture!"
            break
        i = i+1
    cap.release()
    out.release()
def sendEmail():
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = "You Attention is needed"

    body = "Hi, come look at this video"

    msg.attach(MIMEText(body, 'plain'))

    # attaching video to email
    filename = VIDEO_OUTPUT_FILENAME
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attaching photo to email
    filename_photo = "image.jpg"
    attachment_photo = open(filename_photo, 'rb')

    part_photo = MIMEBase('application', 'octet-stream')
    part_photo.set_payload((attachment_photo).read())
    encoders.encode_base64(part_photo)
    part_photo.add_header('Content-Disposition', "attachment; filename= %s" % filename_photo)

    msg.attach(part)
    msg.attach(part_photo)

    print "Sending email"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROM_EMAIL, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(FROM_EMAIL, TO_EMAIL, text)
    server.quit()

def main():
    print strftime("start time: %H:%M:%S")

    setGatewayIP()
    time.sleep(1)
    recordSound()
    # start matlab object
    eng = mat.start_matlab()
    ret = eng.soundtest(WAVE_OUTPUT_FILENAME)
    if int(ret) > 3:
        print "found %d" % ret
        getSnapShot()
        person = findPerson("detected", "image.jpg")
        person = person.split("\\")[1]
        print person, People[person]
        if person != None:
            sendSMS(ret, person)
            getVideo()
            sendEmail()

    print strftime("end time: %H:%M:%S")

if __name__ == "__main__":
    main()
