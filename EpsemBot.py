# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import json
import discord

class EpsemBot(discord.Client):
    async def on_ready(self):
        # Gets guild info (discord server)
        self.guild = discord.utils.get(self.guilds, id=DISCORD_GUILD)

        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n\nServer: {self.guild.name}\nServer id: {self.guild.id}')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="parcials."))

    async def on_message(self, message):

        # Checks if message isn't from the bot itself.
        if message.author == self.user:
            return
        
        # Checks if the message is on the correct server.
        if message.guild != self.guild:
            return

        # Does something if message is correct.
        if message.content == '99!':
            await message.channel.send("Bona nit mal parits")



if __name__ == "__main__":

    # Welcome message
    print("*"*55 + "\n" + " "*10 + "EPSEM BOT - Discord server manager\n" + "*"*55 + "\n\nLoading settings and connecting to Discord...")

    # Loads settings
    with open('bot_settings.json', 'r') as json_token:
        filein = json.loads(json_token.read())
        DISCORD_TOKEN = filein['token']
        DISCORD_GUILD = filein['guild']

    # Runs bot loop
    mainbot = EpsemBot()
    mainbot.run(DISCORD_TOKEN)