# This class manages the users.

from json import loads, dumps

JSON_FILE_PATH = "db/users.json"

class User():
    def __init__(self, id):
        self.id = int(id)
        self.loaduser()

    def mail_command(self, mail):
        '''
        Does something after receiving a mail.
        Returns [a, b, c] depending on:
        a: if this mail is already verified by this user. (True/False)
        b: if user already has a verified mail. (None/Verified mail)
        c: if mail is already verified by another Discord account. (None/Verified Discrod ID) 
        '''

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

    def mail_from(self, mail):
        '''
        Returns the int(user_id) that has the mail, None if mail if free, and self.id if the mail is from the same user.
        '''
        with open(JSON_FILE_PATH) as fin:
            users = loads(fin.read())
        for userid, userinfo in users.items():
            if userinfo['upc-mail-valid']==mail:
                return int(userid)
        return None

    def getuser(self, user):
        '''
        Loads all user variables 
        '''
        self.nickname = user["server-nickname"]
        self.upc_mail_valid = user["upc-mail-valid"]
        self.upc_mail_pending = user["upc-mail-pending"]
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
