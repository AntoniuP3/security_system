from gpiozero import LED
from gpiozero import MotionSensor
from picamera import PiCamera
import datetime
import smtplib, email
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import subprocess
import os.path
import shlex
import time


red_led = LED(17)
red_led.off()
pir = MotionSensor(4)
CAPTURI_PATH = '/home/antoniu/mu_code/Capturi/'
camera = PiCamera()
# filename = CAPTURI_PATH + datetime.datetime.now().isoformat() + '.h264'

titlu = 'Alerta de securitate'
text = """\
Buna ziua!

A fost descoperita prezenta unui intrus. Va rugam sa verificati video-ul atasat acestui email!

Multumim,
securitatepa"""

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'securitatepa2@gmail.com'
PASSWORD = 'fqkrxhifqyomquoh'
RECIEVER_EMAIL = 'antoniuplesca@gmail.com'

session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
session.ehlo()
session.starttls()
session.ehlo()

def video(filepath):
    camera.start_recording(filepath)
    camera.wait_recording(10)
    camera.stop_recording()

def mail(filepath, filename):
    message = MIMEMultipart()
    message ["From"] = USERNAME
    message["To"] = RECIEVER_EMAIL
    message["Subject"] = titlu

    # start = time.time()
    message.attach(MIMEText(text, 'plain'))
    attachment = open(filepath, "rb")

    mimeBase = MIMEBase('application','octet-stream')
    mimeBase.set_payload((attachment).read())

    encoders.encode_base64(mimeBase)
    mimeBase.add_header('Content-Disposition', "attachment; filename= " + filename)

    message.attach(mimeBase)
    text1 = message.as_string()
    # print(f'Video base64 encoding took: {time.time() - start}s')

    # start = time.time()
    session.login(USERNAME, PASSWORD)
    # print(f'Login took: {time.time() - start}s')

    # start = time.time()
    session.sendmail(USERNAME, RECIEVER_EMAIL, text1)
    # print(f'Sending mail took: {time.time() - start}s')
    session.quit()
    print("Email trimis")

while True:
    pir.wait_for_motion()
    print("Miscare detectata")
    red_led.on()
    # camera.capture('/home/antoniu/mu_code/Capturi/ + datetime.datetime.now().isoformat() + '.png')
    # camera.start_recording('/home/antoniu/mu_code/Capturi/Intrus' + datetime.datetime.now().isoformat() + '.h264')
    filename = 'Intrus' + datetime.datetime.now().strftime('%d-%m-%yT%H-%M-%S') + '.h264'
    # filename = 'testwidowslegal.h264'
    filepath = CAPTURI_PATH + filename
    video(filepath)
    command = "ffmpeg -framerate 24 -v 0 -i {} -c copy {}.mp4".format(filepath, os.path.join(CAPTURI_PATH, filename.split('.')[0]))
    # start = time.time()
    subprocess.run(command.split(' '))
    subprocess.run(['rm', filepath])
    # print(f'Converting video and removing the old one took: {time.time() - start}s')
    # start = time.time()
    mail(os.path.join(CAPTURI_PATH, filename.split('.')[0]) + '.mp4', filename.split('.')[0] + '.mp4')
    # print(f'Mailing the video took: {time.time() - start}s')
    # pir.wait_for_no_motion()
    red_led.off()

    print("Miscare oprita")
    # camera.close()
