# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import json
import discord
from emoji import emojize, demojize

# Importing own stuff
import usermanager

# This is now mandatory, and I still don't understand why they did it...
discord.Intents(members=True, messages=True)

class EpsemBot(discord.Client):
    async def send_error_msg(self, channel, duser, error_code):
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
        await sent.delete(delay=10)

    async def send_mail_response(self, dchannel, duser, mail, db_response):
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
        elif db_response==[False, None, None]:
            response_code = 1
        elif db_response[2]==None:
            response_code = 2
        elif db_response[1]==None:
            response_code = 4
        else:
            response_code = 3

        if response_code[2]!=None:
            response_code[2] = super().get_user(response_code[2]).mention

        # Sends mail confirmation discord msg
        # self.send_mail_confirm(self, duser, dchannel, )
        sent = await dchannel.send(emojize(responses[0].format(duser.mention, mail, response_code[1], response_code[2]), use_aliases=True))

        if response_code!=0:
            # Adds thumbs up and down emoji reactions
            await sent.add_reaction( emoji=emojize( ":thumbsup:", use_aliases=True ) )
            await sent.add_reaction( emoji=emojize( ":thumbsdown:", use_aliases=True ) )

        # Deletes the message if isn't reacted after 30s. If it is, on_raw_reaction_add() will delete it before.
        await sent.delete(delay=30)

    async def update_roles(self, user_id, new_roles, remove_student=False):
        '''
        Given a user id and all the roles, removes ALL subject roles and puts all new roles.
        '''
        if not remove_student: # Adds student to a role needed, in case.
            new_roles += "estudiant"

        member = self.guild.get_member(user_id)
        actual_roles = [ r.id for r in member.roles ]

        for rolename, roleid in ROLES_ID.items(): # Every possible subj role
            if rolename in new_roles: # If user needs to have the role
                if roleid not in actual_roles: # If user didn't have that role already
                    await member.add_roles(self.guild.get_role(roleid))

            else:
                if roleid in actual_roles: # If user has this role, and don't needed.
                    await member.remove_roles(self.guild.get_role(roleid))

    async def on_ready(self):

        # Gets guild info (discord server)
        self.guild = discord.utils.get(self.guilds, id=GUILD)

        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n\nServer: {self.guild.name}\nServer id: {self.guild.id}')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="parcials."))

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
                if len(username.split('@'))!=1 and len(username.split('.'))<2:
                    # User contains domain or doesn't contain dots.
                    self.send_error_msg(message.channel, message.author, 2)
                    return

                # Gets domain
                is_prof = cnt[0].lower()=='prof'
                mail = username + ('@estudiantat.upc.edu' if is_prof else '@upc.edu')

                # Checks availability and gets the response from db.
                # This respnse is sended automaticly to send_mail_response.
                user = usermanager.User(message.author.id)
                self.send_mail_response(self, message.channel, message.author, mail, user.mail_command(mail))

            elif cnt[0].lower() == 'code' and len(cnt)==2:
                # Code entered
                try:
                    code = int(cnt[1])
                except ValueError:
                    # Sends error response if code isn't a number.
                    self.send_error_msg(message.channel, message.author, 1)
                    return

                # Sends error response if code isnt XXXXXX where X is a number or code is a float.
                if len(cnt[1])!=6 or float(cnt[1]) != code:
                    self.send_error_msg(message.channel, message.author, 1)
                    return

                # Checkss if code was needed and valid.
                user = usermanager.User(message.author.id)
                if not user.code_command(code):
                    self.send_error_msg(message.channel, message.author, 3)
                else:
                    self.update_roles(message.author.id, user.quadrimesters + user.subjects_added)
            else:
                # Sends error response
                self.send_error_msg(message.channel, message.author, 0)
                return

        # Does something if message is correct.
        elif len(message.mentions)>2:
            await message.channel.send("Ep! No et passis etiquetant a tanta gent!")

    async def on_raw_reaction_add(self, payload):
        msg = payload.message_id
        usr = payload.user_id
        emoji = payload.emoji.name
        ch = payload.channel_id
        member = payload.member

        # Checking if is a role message.
        if msg == ROLES_MSGS['q1']:
            await member.add_roles(self.guild.get_role(ROLES_ID['q1']))
            if emoji==emojize(":one:"):
                await member.add_roles(self.guild.get_role(ROLES_ID['q1-fisica']))
            if emoji==emojize(":two:"):
                await member.add_roles(self.guild.get_role(ROLES_ID['q1-fonaments']))
        if msg == ROLES_MSGS['q2']:
            await member.add_roles(self.guild.get_role(ROLES_ID['q2']))
            if emoji==emojize(":one:"):
                await member.add_roles(self.guild.get_role(ROLES_ID['q2-sociologia']))
            if emoji==emojize(":two:"):
                await member.add_roles(self.guild.get_role(ROLES_ID['q2-teatre']))

    async def on_raw_reaction_remove(self, payload):
        msg = payload.message_id
        usr = payload.user_id
        emoji = payload.emoji.name
        ch = payload.channel_id
        member = await self.guild.fetch_member(usr)

        # Checking if is a role message.
        if msg == ROLES_MSGS['q1']:
            await member.remove_roles(self.guild.get_role(ROLES_ID['q1']))
            if emoji=="1️⃣":
                await member.remove_roles(self.guild.get_role(ROLES_ID['q1-fisica']))
            if emoji=="2️⃣":
                await member.remove_roles(self.guild.get_role(ROLES_ID['q1-fonaments']))
        if msg == ROLES_MSGS['q2']:
            await member.remove_roles(self.guild.get_role(ROLES_ID['q2']))
            if emoji=="1️⃣":
                await member.remove_roles(self.guild.get_role(ROLES_ID['q2-sociologia']))
            if emoji=="2️⃣":
                await member.remove_roles(self.guild.get_role(ROLES_ID['q2-teatre']))

    
if __name__ == "__main__":

    # Welcome message
    print("\n" + "*"*55 + "\n" + " "*10 + "EPSEM BOT - Discord server manager\n" + "*"*55 + "\n\nLoading settings and connecting to Discord...")

    # Loads settings
    with open('bot_settings.json', 'r') as json_file:
        filein = json.loads(json_file.read())
        TOKEN= filein['token']
        GUILD = filein['guild']
        ROLES_ID = filein['roles-id']
        ROLES_MSGS = filein['roles-msgs']
        TC_ID = filein['text-channels-id']
        VC_ID = filein['voice-channels-id']

    # Runs bot loop
    mainbot = EpsemBot()
    mainbot.run(TOKEN)
