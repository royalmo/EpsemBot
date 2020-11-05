import smtplib
import json


def send_mail(to, link):
    '''
    Given a destination mail adress and the verification link to insert on the mail, this function sends the mail using gmail_settings.json.
    
    Returns True if succeeded and False if failed.

    Both parameters must be strings: send_mail('eric@ericroy.net', 'https://ericroy.net')
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
    mail = f"From: {GMAIL_USR}\nTo: {to}\nSubject: {SUBJECT}\n\n{BODY.format(link)}"

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
    link = input("Introduce verification link adresss: ")

    print( ( "\nMail successfully sent to " + to ) if send_mail(to, link) else "\nSomething went wrong while sending your mail." )