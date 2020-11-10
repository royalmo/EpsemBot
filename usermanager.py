# MAIN FILE IS EpsemBot.py
# This class and functions below manages the users.

from json import loads, dumps
from send_mail import send_mail
from random import randint
from pathlib import Path

JSON_FILE_PATH = "db/users.json"
THIS_FILE_FOLDER = str(Path(__file__).parent.absolute()) + "/"

class User():
    def __init__(self, id):
        self.id = int(id)
        self.loaduser()

    def loaduser(self):
        '''
        Returns the dict of the user info, or -1 if not found.
        '''
        with open(THIS_FILE_FOLDER + JSON_FILE_PATH) as fin:
            users = loads(fin.read())
        
        if str(self.id) in users.keys():
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
        self.subjects_added = user["subjects-added"]

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
            "verification-code": 0,
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
            "upc-mail-expired": self.upc_mail_expired,
            "mail-status": self.mail_status,
            "verification-code": self.verification_code,
            "subjects-selected": self.subjects_selected,
            "quadrimesters": self.quadrimesters,
            "subjects-added": self.subjects_added
        }

        with open(THIS_FILE_FOLDER + JSON_FILE_PATH, "r+") as jfile:
            users = loads(jfile.read())
            users[str(self.id)] = to_save_user
            jfile.seek(0)
            jfile.write(dumps(users))
            jfile.truncate()

    def mail_command(self, mail):
        '''
        Does some checks after receiving a mail.
        
        Adds mail to self.upc_mail_pending if it can be verified.

        Returns [a, b, c] depending on:
        - a: if this mail is already verified by this user. (True/False)
        - b: if user already has a verified mail. (None/Verified mail)
        - c: if mail is already verified by another Discord account. (None/Verified Discrod ID) 
        '''
        if self.upc_mail_valid == mail:
            return [True, None, None]

        # If mail is from another user mail is new or user has another mail, this means that this mail can be verified, so let's save it.
        self.upc_mail_pending = mail
        self.saveuser()

        # Checks the previous things mentioned above, and returns the values.
        actualmail = self.upc_mail_valid if self.upc_mail_valid!="" else None
        dbmail = mail_from(mail)

        return [False, actualmail, dbmail]

    def send_code(self):
        '''
        Sends a verification code to the user, and updates status and json file.
        Returns True if succeeded, False if not.
        '''
        self.verification_code = randint( 100000, 999999 )
        self.mail_status = 3 if self.mail_status<5 else 8
        self.saveuser()

        return send_mail(self.upc_mail_pending, self.verification_code, get_name(self.upc_mail_pending))

    def code_command(self, code):
        '''
        CODE HAS TO BE AN INTEGER!
        Given the code and the user, verifies if code is correct, and updates things if necessary.
        Returns [a, b] where:
        - a: True/False depending of code verification.
        - b: None/user_id that needs to have their roles removed.
        '''
        # If code not asked
        if self.mail_status not in [3, 4, 8]:
            return [False, None]
        
        # If code is incorrect
        if code!=self.verification_code:
            self.mail_status = 4 if self.mail_status in [3, 4] else 8
            self.saveuser()
            return [False, None]

        # Updates mail
        self.mail_status = 5
        self.upc_mail_valid = self.upc_mail_pending
        self.upc_mail_pending = ""
        self.upc_mail_expired = ""

        # Removes old user (if any)
        remove_roles = self.expire_mail(self.upc_mail_valid)

        # Add student roles to the user.
        self.update_roles()

        # Change student username (NOT Discord nickname, this has to be done from EpsemBot.py)
        self.nickname = get_name(self.upc_mail_valid)

        # Save and return
        self.saveuser()
        return [True, remove_roles]

    def expire_mail(self, mail):
        '''
        Returns the id of the mail to remove the roles, and change db things of that user. None if user to downgrade doesn't exist or is self.
        '''
        mail_author_id = mail_from(mail)
        if mail_author_id in [None, self.id]:
            return None

        # Changes some settings for the downgraded user
        downgrade = User(mail_author_id)
        downgrade.nickname = downgrade.nickname + '(Old)'
        downgrade.upc_mail_expired = downgrade.upc_mail_valid
        downgrade.upc_mail_valid = ""
        downgrade.mail_status = 6
        downgrade.quadrimesters = []
        downgrade.subjects_added = []
        downgrade.saveuser()

        # Returns that user id so settings can be applied.
        return mail_author_id

    def update_roles(self):
        '''
        Updates the roles to the student, does not return anything.
        '''
        if self.mail_status in [5, 7, 8, 9]:
            # Picks up the 6 first subjects selected.
            self.subjects_added = self.subjects_selected[:6]

            # Selects witch quadrimesters to add depending on the subjects selected.
            self.quadrimesters = []
            for subject in self.subjects_added:
                if subject[:2] not in self.quadrimesters:
                    self.quadrimesters.append(subject[:2])
        else:
            self.quadrimesters = []
            self.subjects_added = []
        self.saveuser()

    def role_clicked(self, role_internal_id, selected):
        '''
        What happens when the user reacts to a emoji subject? This function is called. Doesn't return anything, just work out what to do with that role click.

        Role_internal_id: find that in bot_settings.json (EG: "q1-fisica")
        Selected (T/F): if the emoji reaction was selected or disselected.
        '''
        if selected and (role_internal_id not in self.subjects_selected):
            self.subjects_selected.append(role_internal_id)
            self.update_roles()
        if (not selected) and (role_internal_id in self.subjects_selected):
            self.subjects_selected.remove(role_internal_id)
            self.update_roles()
        

# User actions, but that they don't depend of the user.

def mail_from(mail):
    '''
    Returns the int(user_id) that has the mail, None if mail if mail is free to take.
    '''
    with open(THIS_FILE_FOLDER + JSON_FILE_PATH) as fin:
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

def get_name(username):
    '''
    Given a email or a username, returns the capitalized name for the user.
    This funciton doesn't verify that a username is valid or not.
    The username should be something like name.surname.othersurname .
    '''
    username = username.split('@')[0] #Removes mail domain if it has some.
    
    return ' '.join([word.capitalize() for word in username.split('.')])
