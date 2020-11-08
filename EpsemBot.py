# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import json
import discord

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
                await message.channel.send('user')
            else:
                if len(cnt)==6:
                    await message.channel.send('correct code')
                else:
                    await message.channel.send('incorrect code')

        # Does something if message is correct.
        if len(message.mentions)>2:
            await message.channel.send("Ep! No et passis etiquetant a tanta gent!")

    async def on_raw_reaction_add(self, playload):
        DM_MSG = 773846606792491029
        DM_EMJ = "👍"

        msg = playload.message_id
        usrid = playload.user_id
        emoji = playload.emoji

        if msg == DM_MSG and emoji.name == DM_EMJ:
            usr = self.get_user(usrid)

    async def on_raw_reaction_remove(self, playload):
        DM_MSG = 773846606792491029
        DM_EMJ = "👍"

        msg = playload.message_id
        usr = playload.user_id
        emoji = playload.emoji

        if msg == DM_MSG and emoji.name == DM_EMJ:
            print(usr)

    
if __name__ == "__main__":

    # Welcome message
    print("\n" + "*"*55 + "\n" + " "*10 + "EPSEM BOT - Discord server manager\n" + "*"*55 + "\n\nLoading settings and connecting to Discord...")

    # Loads settings
    with open('bot_settings.json', 'r') as json_file:
        filein = json.loads(json_file.read())
        TOKEN= filein['token']
        GUILD = filein['guild']

    # Runs bot loop
    mainbot = EpsemBot()
    mainbot.run(TOKEN)
