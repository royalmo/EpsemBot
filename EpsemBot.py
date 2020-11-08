# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import json
import discord

# Importing own stuff
import usermanager

intents = discord.Intents(members=True, messages=True)

class EpsemBot(discord.Client):
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
        #     await msg.add_reaction( emoji="1️⃣" )
        #     await msg.add_reaction( emoji="2️⃣" )
        # return

        # Checks and does something if message is from the 'welcome' channel
        if message.channel.id==773689013542060064:
            cnt = message.content.split()
            helpch = super().get_channel(773929041220075563)
            await message.delete()
            if cnt[0].lower() in ['user', 'code'] and len(cnt)==2:
                cnt = cnt[1]
            elif len(cnt)==1:
                cnt = cnt[0]
            else:
                sent = await message.channel.send(f"No entenc el que dius {message.author.mention}, torna-ho a intentar, o demana {helpch.mention} .")
                await sent.delete(delay=10)
                return

            try:
                cnt = int(cnt)
            except ValueError:
                if len(cnt.split('.'))>1:
                    sent = await message.channel.send(f'{message.author.mention}: enviar mail a `{cnt}@estudiantat.upc.edu` (👍/👎)? Si el mail és `{cnt}@upc.edu`, reacciona amb 🤏')
                    await sent.add_reaction( emoji="👍" )
                    await sent.add_reaction( emoji="👎" )
                    await sent.add_reaction( emoji="🤏" )
                    await sent.delete(delay=30)
                else:
                    sent = await message.channel.send(f"No entenc el que dius {message.author.mention}, torna-ho a intentar, o demana {helpch.mention} .")
                    await sent.delete(delay=10)
                    return
                    
            else:
                if len(cnt)==6:
                    await message.channel.send('correct code')
                else:
                    await message.channel.send('incorrect code')

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
            if emoji=="1️⃣":
                await member.add_roles(self.guild.get_role(ROLES_ID['q1-fisica']))
            if emoji=="2️⃣":
                await member.add_roles(self.guild.get_role(ROLES_ID['q1-fonaments']))
        if msg == ROLES_MSGS['q2']:
            await member.add_roles(self.guild.get_role(ROLES_ID['q2']))
            if emoji=="1️⃣":
                await member.add_roles(self.guild.get_role(ROLES_ID['q2-sociologia']))
            if emoji=="2️⃣":
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
        ROLES_ID = filein["roles-id"]
        ROLES_MSGS = filein["roles-msgs"]
        TC_ID = filein["text-channels-id"]
        VC_ID = filein["voice-channels-id"]

    # Runs bot loop
    mainbot = EpsemBot()
    mainbot.run(TOKEN)
