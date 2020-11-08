# MAIN FILE IS EpsemBot.py
# This class and functions below manages the users.

from json import loads, dumps
from send_mail import send_mail
from random import ranidnt

JSON_FILE_PATH = "db/users.json"

class User():
    def __init__(self, id):
        self.id = int(id)
        self.loaduser()

    def loaduser(self):
        '''
        Returns the dict of the user info, or -1 if not found.
        '''
        with open(JSON_FILE_PATH) as fin:
            users = loads(fin.read())
        
        if self.id in users.keys():
            self.getuser( users[str(self.id)] )
        else:
            self.newuser()

    def getuser(self, user):
        '''
        Loads all user variables 
        '''
        self.nickname = user["server-nickname"]
        self.upc_mail_valid = user["upc-mail-valid"]
        self.upc_mail_pending = user["upc-mail-pending"]
        self.upc_mail_expired = user["upc-mail-expired"]
        self.mail_status = user["mail-status"]
        self.verification_code = user["verification-code"]
        self.subjects_selected = user["subjects-selected"]
        self.quadrimesters = user["quadrimesters"]
        self.subjects_added = user["subjects_added"]

    def newuser(self):
        '''
        Creates a new user.
        '''
        user = {
            "server-nickname": "",
            "upc-mail-valid": "",
            "upc-mail-pending": "",
            "upc-mail-expired": "",
            "mail-status": 0,
            "verifiaction-code": 0,
            "subjects-selected": [],
            "quadrimesters": [],
            "subjects-added": []
        }
        self.getuser(user)
        self.saveuser()

    def saveuser(self):
        '''
        Saves the user info to JSON_FILE_PATH.
        '''
        to_save_user = {
            "server-nickname": self.nickname,
            "upc-mail-valid": self.upc_mail_valid,
            "upc-mail-pending": self.upc_mail_pending,
            "upc-mail-epired": self.upc_mail_expired,
            "mail-status": self.mail_status,
            "verifiaction-code": self.verification_code,
            "subjects-selected": self.subjects_selected,
            "quadrimesters": self.quadrimesters,
            "subjects-added": self.subjects_added
        }

        with open(JSON_FILE_PATH, "w+") as jfile:
            users = loads(jfile.read())
            users[str(self.id)] = to_save_user
            jfile.write(dumps(users))

    def mail_command(self, mail):
        '''
        Does something after receiving a mail.
        Returns [a, b, c] depending on:
        a: if this mail is already verified by this user. (True/False)
        b: if user already has a verified mail. (None/Verified mail)
        c: if mail is already verified by another Discord account. (None/Verified Discrod ID) 
        '''
        if self.upc_mail_valid == mail:
            return [True, None, None]

        actualmail = self.upc_mail_valid if self.upc_mail_valid!="" else None
        dbmail = mail_from(mail)

        if dbmail==None:
            return [False, actualmail, dbmail]

    def send_code(self):
        '''
        Sends a verification code to the user, and updates status and json file.
        Returns True if succeeded, False if not.
        '''
        self.verification_code = ranidnt( 100000, 999999 )
        self.mail_status = 3 if self.mail_status<3 else 8
        self.saveuser()

        return send_mail(self.upc_mail_pending, self.verification_code, self.username)

    def code_command(self, code):
        '''
        CODE HAS TO BE AN INTEGER!
        Given the code and the user, verifies if code is correct, and updates things if necessary. Returns True/False depending of code verification.
        '''
        if self.mail_status not in [3, 8]:
            return False
        


        return code==self.verification_code

# User actions, but that they don't depend of the user.

def mail_from(mail):
    '''
    Returns the int(user_id) that has the mail, None if mail if free, and self.id if the mail is from the same user.
    '''
    with open(JSON_FILE_PATH) as fin:
        users = loads(fin.read())
    for userid, userinfo in users.items():
        if userinfo['upc-mail-valid']==mail:
            return int(userid)
    return None

def is_upc_mail(mail):
    '''
    Returns True/False if a mail is nom.congnom.more@upc.edu or @estudiantat.upc.edu.
    '''
    if len(mail.split()) != 1 or len(mail.split('@'))!=2:
        return False

    [user, domain] = mail.split('@')
    
    if domain not in ['estudiantat.upc.edu', 'upc.edu']:
        return False
    
    return len(user.split('.'))>=2
