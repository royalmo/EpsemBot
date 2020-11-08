# MAIN FILE IS EpsemBot.py
# This file manages send_mail(), that is usefull when verifying user mails.

import smtplib
import json

def send_mail(to, code, name=""):
    '''
    Given a destination mail adress and the verification code to insert on the mail, this function sends the mail using gmail_settings.json.

    A name can also be given, to make the user feel we concern about security.
    
    Returns True if succeeded and False if failed.

    Both parameters must be strings: send_mail('eric@ericroy.net', '937485')
    '''
    # Loading variables
    with open("gmail_settings.json", "r") as fin:
        json_raw = json.loads(fin.read())

        HOST = json_raw["host"]
        PORT = json_raw["port"]

        GMAIL_USR = json_raw["gmail-usr"]
        GMAIL_PWD = json_raw["gmail-pwd"]

        SUBJECT = json_raw["subject"]
        BODY = json_raw["body"]

    # Creating mail text
    mail = f'From: "EPSEM-BOT" <{GMAIL_USR}>\nTo: {to}\nSubject: {SUBJECT}\n\n{BODY.format(name, code)}'

    # Sends mail (except if no connection, google servers down, etc.)
    try:
        server = smtplib.SMTP_SSL(HOST, PORT)
        server.ehlo()
        server.login(GMAIL_USR, GMAIL_PWD)
        server.sendmail(GMAIL_USR, to, mail)
        server.close()

        return True
    except:
        return False

# Example program, for testing
if __name__=="__main__":

    to = input("Introduce *to* mail adress: ")
    name = input("Enter username: ")
    code = input("Introduce verification code to send: ")

    print( ( "\nMail successfully sent to " + to ) if send_mail(to, code, name) else "\nSomething went wrong while sending your mail." )