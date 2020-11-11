# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import discord
from json import loads, dumps
from emoji import emojize, demojize

# Importing own stuff
import usermanager

# This is now mandatory, and I still don't understand why they did it...
# discord.Intents(members=True, messages=True) #THIS LINE DOESN'T WORK
intents = discord.Intents.default() #THESE 3 LINES YES
intents.members = True
intents.messages = True

class EpsemBot(discord.Client):
    async def send_error_msg(self, channel, duser, error_code, autodestruct=15):
        '''
        Given a channel to send the message, the discord user to ping and the error code, it returns a simple self-destructing error message.

        ERROR CODES:
        - 0: Unknown command (if user didn't entered 'user user.name' or 'code something')
        - 1: Code isn't a len 6 integer.
        - 2: Username doesn't have any dot (.) if it's your username, get help.
        - 3: Code is int but does not match with email.
        '''
        errors = [
            "No entenc el que dius {0}, torna-ho a intentar, o demana {1}.", "El codi que has entrat no consta de 6 xifres {0}, torna-ho a intentar, o demana {1}.",
            "El nom d'usuari ha de ser en format nom.cognom {0}, torna-ho a intentar. Si el teu usuari no inclou cap punt (.) entre els noms i cognoms, demana {1}.",
            "El codi que has entrat no concorda amb el codi enviat per mail, o simplement no has rebut cap mail {0}, torna-ho a intentar, o demana {1}."
            ]

        helpch = super().get_channel(TC_ID['help-ch'])
        sent = await channel.send(errors[error_code].format(duser.mention, helpch.mention))
        await sent.delete(delay=autodestruct)

    async def send_mail_response(self, dchannel, duser, mail, db_response, autodestruct=30):
        '''
        Given the discord channel, the discord user, the mail entered, and the response from the user database, sends a response to the chat.

        Remember how the response returns [a, b, c] depending on:
        - a: if this mail is already verified by this user. (True/False)
        - b: if user already has a verified mail. (None/Verified mail)
        - c: if mail is already verified by another Discord account. (None/Verified Discrod ID)
        '''
        responses = [
            # 0: When user has this mail already verified (only case that reactions aren't needed) response = [True, None, None]
            '{0}: ja tens verificat el correu `{1}`!',
            # 1: When user doesn't have mail, and mail is unique:
            # [False, None, None]
            '{0}: enviar mail a `{1}`? (:thumbsup:/:thumbsdown:)',
            # 2: When user has already a mail, but mail is unique.
            # [False, verified_mail, None]
            '{0}: enviar mail a `{1}`? (:thumbsup:/:thumbsdown:)\nATENCI\u00d3: ja tens verificat el correu `{2}` amb el teu compte de Discord.\nSi continues, es canviar\u00e0 el mail un cop l\'hagis verificat',
            # 3: When user has already a mail, and mail is verified by other.
            # [False, verified_mail, other_id]
            '{0}: enviar mail a `{1}`? (:thumbsup:/:thumbsdown:)\nATENCI\u00d3: ja tens verificat el correu `{2}` amb el teu compte de Discord, i el correu {1} est\u00e0 ennla\u00e7at amb {3}.\nSi continues, es canviar\u00e0 el mail un cop l\'hagis verificat, i {3} perdr\u00e0 l\'acc\u00e9s al servidor.',
            # 4: When user has no mail, and mail is verified by other.
            # [False, None, other_id]
            '{0}: enviar mail a `{1}`? (:thumbsup:/:thumbsdown:)\nATENCI\u00d3: El correu {1} est\u00e0 ennla\u00e7at amb {3}.\nSi continues, es canviar\u00e0 el mail un cop l\'hagis verificat, i {3} perdr\u00e0 l\'acc\u00e9s al servidor.'
        ]

        if db_response == [True, None, None]:
            response_code = 0
        elif db_response == [False, None, None]:
            response_code = 1
        elif db_response[2] == None:
            response_code = 2
        elif db_response[1] == None:
            response_code = 4
        else:
            response_code = 3

        if db_response[2]!=None:
            db_response[2] = super().get_user(db_response[2]).mention

        # Sends mail confirmation discord msg
        # self.send_mail_confirm(self, duser, dchannel, )
        sent = await dchannel.send(emojize(responses[response_code].format(duser.mention, mail, db_response[1], db_response[2]), use_aliases=True))

        if response_code!=0:
            # Adds thumbs up and down emoji reactions
            await sent.add_reaction( emoji=emojize( ":thumbsup:", use_aliases=True ) )
            await sent.add_reaction( emoji=emojize( ":thumbsdown:", use_aliases=True ) )

        # Deletes the message if isn't reacted after 30s. If it is, on_raw_reaction_add() will delete it before.
        await sent.delete(delay=autodestruct)

    async def send_answer(self, duser, dchannel, msg_code, autodestruct=10):
        '''
        Given a Discord user, a Discord channel, and a code, the bot sends a message to the code and pings the user.

        MESSAGE CODES:
        - 0: Mail sent was successful.
        - 1: Mail sent has been aborted by user (user pressed :thumbsdown:).
        - 2: Mail sent had an error. (For the moment, unknown error)
        - 3: Verification code entered correctly.
        '''
        msgs = [
            "S'ha envat correctament el mail amb el codi de verificaci\u00f3 {0}.\nComprova la teva safata d'entrada.",
            "S'ha cancel\u00b7lat l'enviament del missatge, {0}.\nPots tornar a introduir un correu electr\u00f2nic seguint les instruccions anteriors.",
            "Hi ha hagut algun error en l'enviament del missatge. Verifica que haguis introduit correctament l'usuari i torna-ho a intentar, {0}.",
            "Enhorabona, {0}! Ja pots accedir al servidor! Recorda de configurar les teves {1} per a tenir els canals espec\u00edfics"
            ]

        subjectmention = self.guild.get_channel(TC_ID['subjects-ch']).mention

        sent = await dchannel.send(msgs[msg_code].format(duser.mention, subjectmention))
        await sent.delete(delay=autodestruct)

    async def update_roles(self, user_id, new_roles=[], nickname=None, remove_student=False):
        '''
        Given a user id and all the roles, removes ALL subject roles and puts all new roles.
        '''
        member = await self.guild.fetch_member(user_id)
        actual_roles = [ r.id for r in member.roles ]
        user = super().get_user(user_id)

        if not remove_student: # Adds student to a role needed, in case.
            new_roles.append("estudiant")
            if nickname != None:
                await self.edit_nickname(member, nickname)
        else:
            await self.edit_nickname(member, (member.nick if member.nick!=None else user.name) + " (Old)")

        for rolename, roleid in ROLES_ID.items(): # Every possible subj role
            if rolename in new_roles: # If user needs to have the role
                if roleid not in actual_roles: # If user didn't have that role already
                    await member.add_roles(self.guild.get_role(roleid))

            else:
                if roleid in actual_roles: # If user has this role, and don't needed.
                    await member.remove_roles(self.guild.get_role(roleid))

    async def remove_roles(self, user_id):
        '''
        Removes all subject_roles that user_id has. Uses update_roles().
        '''
        await self.update_roles(user_id, remove_student=True)

    async def edit_nickname(self, member, new_nick):
        '''
        Edits the member nickname in the server. Aborts operation in silence if it has a Forbidden error (editing admin's name).
        Doesn't return anything.
        '''
        try:
            await member.edit(nick=new_nick)
        except discord.errors.Forbidden:
            print(f"Abborted nickname change for user_id: {member.id}. Permission dennied.")

    async def on_ready(self):

        # Gets guild info (discord server)
        self.guild = discord.utils.get(self.guilds, id=GUILD)

        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n\nServer: {self.guild.name}\nServer id: {self.guild.id}')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="parcials."))

        # Sets own member
        self.own_member = await self.guild.fetch_member(self.user.id)

    async def on_message(self, message):

        # Checks if message isn't from the bot itself, is from the correct server, and it is plain text. 
        if message.author == self.user or message.guild != self.guild or message.type != discord.MessageType.default:
            return

        # DO THIS WHEN YOU NEED TO PUT REACTION ON MESSAGES
        # async for msg in message.channel.history():    
        #     await msg.add_reaction(emoji=emojize(":one:", use_aliases=True))
        #     await msg.add_reaction(emoji=emojize(":two:", use_aliases=True))
        # return

        # Checks and does something if message is from the 'welcome' channel
        if message.channel.id==TC_ID['welcome-ch']:
            cnt = message.content.split()
            await message.delete()
            if cnt[0].lower() in [ 'user', 'prof' ] and len(cnt)==2:

                # User entered
                username = cnt[1]
                if len(username.split('@'))!=1 or len(username.split('.'))<2:
                    # User contains domain or doesn't contain dots.
                    await self.send_error_msg(message.channel, message.author, 2)
                    return

                # Gets domain
                is_prof = cnt[0].lower()=='prof'
                mail = username + ('@upc.edu' if is_prof else '@estudiantat.upc.edu')

                # Checks availability and gets the response from db.
                # This respnse is sended automaticly to send_mail_response.
                user = usermanager.User(message.author.id)
                await self.send_mail_response(message.channel, message.author, mail, user.mail_command(mail))

            elif cnt[0].lower() == 'code' and len(cnt)==2:
                # Code entered
                try:
                    code = int(cnt[1])
                except ValueError:
                    # Sends error response if code isn't a number.
                    await self.send_error_msg(message.channel, message.author, 1)
                    return

                # Sends error response if code isnt XXXXXX where X is a number or code is a float.
                if len(cnt[1])!=6 or float(cnt[1]) != code:
                    await self.send_error_msg(message.channel, message.author, 1)
                    return

                # Checkss if code was needed and valid.
                user = usermanager.User(message.author.id)
                actions = user.code_command(code)
                if not actions[0]:
                    await self.send_error_msg(message.channel, message.author, 3)
                else:
                    await self.update_roles(message.author.id, user.quadrimesters + user.subjects_added, user.nickname)
                    if actions[1]!=None: # If some user needs to have their roles removed.
                        await self.remove_roles(actions[1])
                    await self.send_answer(message.author, message.channel, 3)

            else:
                # Sends error response
                await self.send_error_msg(message.channel, message.author, 0)
            
            return # To prevent this function from doing other things

        # Here you can append other funcions in on_message()

    async def on_raw_reaction_add(self, payload):
        
        # Getting some basic information
        duser = super().get_user(payload.user_id)
        emoji = payload.emoji.name
        channel = self.guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        member = payload.member

        # Checking if it's a mail confirmation message.
        if channel.id == TC_ID['welcome-ch'] and duser in msg.mentions:
            await msg.delete()
            if emoji==emojize( ":thumbsdown:", use_aliases=True ):
                await self.send_answer( duser, channel, 1 )
            else:
                db_user = usermanager.User(duser.id)
                success = db_user.send_code()
                await self.send_answer( duser, channel, 0 if success else 2 )

        # Checking if is a role message.
        if channel.id == TC_ID['subjects-ch']:
            dbuser = usermanager.User(duser.id)
            for rolekey, rolemsgid in ROLES_MSGS.items():
                if rolemsgid == msg.id:
                    for subject, emojiname in ROLE_SCHEMA[rolekey].items():
                        if emoji == emojize( emojiname, use_aliases=True ):
                            subject_id = rolekey + '-' + subject
                            dbuser.role_clicked(subject_id, selected = True)
            await self.update_roles(duser.id, dbuser.quadrimesters + dbuser.subjects_added)

    async def on_raw_reaction_remove(self, payload):

        # Getting some basic information
        duser = super().get_user(payload.user_id)
        emoji = payload.emoji.name
        channel = self.guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        member = await self.guild.fetch_member(duser.id)

        # Checking if is a role message.
        if channel.id == TC_ID['subjects-ch']:
            dbuser = usermanager.User(duser.id)
            for rolekey, rolemsgid in ROLES_MSGS.items():
                if rolemsgid == msg.id:
                    for subject, emojiname in ROLE_SCHEMA[rolekey].items():
                        if emoji == emojize( emojiname, use_aliases=True ):
                            subject_id = rolekey + '-' + subject
                            dbuser.role_clicked(subject_id, selected = False)
            await self.update_roles(duser.id, dbuser.quadrimesters + dbuser.subjects_added)

if __name__ == "__main__":

    # Welcome message
    print("\n" + "*"*55 + "\n" + " "*10 + "EPSEM BOT - Discord server manager\n" + "*"*55 + "\n\nLoading settings and connecting to Discord...")

    # Loads settings
    with open(usermanager.THIS_FILE_FOLDER + 'bot_settings.json') as json_file:
        filein = loads(json_file.read())
        TOKEN= filein['token']
        GUILD = filein['guild']
        ROLES_ID = filein['roles-id']
        ROLES_MSGS = filein['roles-msgs']
        TC_ID = filein['text-channels-id']
        VC_ID = filein['voice-channels-id']
        ROLE_SCHEMA = filein['role-schema']

    # Runs bot loop
    mainbot = EpsemBot(intents=intents)
    mainbot.run(TOKEN)
