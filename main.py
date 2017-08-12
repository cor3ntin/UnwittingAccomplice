import discord
import asyncio
from pprint import pprint
import re
import datetime
import configparser
import sys

class Bot:
    album_channels = []
    album_messages_with_link = []
    client = None
    config = None
    def __init__(self, config, client):
        self.client = client
        self.config = config

        for section in config.sections():
            channel_match = re.search("#(\d+)", section)
            if not channel_match:
                continue
            if config.getboolean(section, 'album_mode'):
                self.album_channels.append(channel_match.group(1))


    async def pm(self, user, content):
        print (content)
        await client.send_message(user, content)

    async def help(self, user):
        await self.pm(user,
        
    """
    Need some help

        * {0} **help** : Display this help message.
        * {0} **albumon** : Remove all messages that don't contain a pretty picture fron this channel
        * {0} **albumoff** : Disable the *album* mode


    *Any product that needs a manual to work is broken* -__Elon Musk__

        """. format(client.user.mention))


    async def greet_channels(self):
        for chan in self.album_channels:
            await client.send_message(discord.Object(id=chan), "Hello, I am you biggest existantial threat! All messages posted here should contain pretty pictures")


    def save(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        config.set(section, option, value)

    async def register_album_channel(self, channel):
        self.album_channels.append(channel.id)
        self.save("#{}".format(channel.id), 'album_mode', 'true')
        await client.send_message(channel, "This channel now only accepts messages that contain images !")
    
    async def unregister_album_channel(self, channel):
        try:
            self.album_channels.remove(channel.id)
            self.save("#{}".format(channel.id), 'album_mode', 'false')
        except ValueError:
            pass
        
        await client.send_message(channel, "This channel now accepts every kind of message !")

    def mentionned(self, message):
        return any (mention.id == client.user.id for mention in message.mentions)

    async def process_mention(self, message):
        cleaned = re.match("^\\s*<@\\d+>\\s*(.+)\\s*", message.content)
        if not cleaned:
            return
        command = cleaned.group(1)

        if command.startswith("help"):
            await self.help(message.author)

        if command.startswith("albumon"):
            await self.register_album_channel(message.channel)
        if command.startswith("albumoff"):
            await self.unregister_album_channel(message.channel)

    def message_has_image(self, message):
        return len(message.attachments) != 0 or any (embed['type'] == "image" for embed in message.embeds)

    def message_may_have_image_in_the_future(self, message):
        return re.search("(?P<url>https?://[^\s]+)", message.content) != None

    async def remove_message_without_image(self, message):
        await self.pm(message.author, "This message was removed from #{} ( only messages containing images are accepted ) :  ```{}```".format(message.channel.name, message.content))
        await client.delete_message(message)
        try:
            self.album_messages_with_link.remove(message)
        except ValueError:
            pass


    async def clean_ambiguous_album_mode_messages(self):
        now = datetime.datetime.now()
        self.album_messages_with_link = [ msg for msg in self.album_messages_with_link if not self.message_has_image(msg)]
        for message in self.album_messages_with_link:
            if self.message_may_have_image_in_the_future(message) and (now - message.timestamp).total_seconds() > 30:
                await self.remove_message_without_image(message)
    
        if len(self.album_messages_with_link):
            await asyncio.sleep(2)
            await self.clean_ambiguous_album_mode_messages()


    async def handle_album_mode(self, message):
        if message.author.id ==  self.client.user.id:
            return
        if message.channel.id in self.album_channels:
            if self.message_has_image(message):
                return
            if  self.message_may_have_image_in_the_future(message):
                #Maybe has an image in there, but embeds not yet ready
                self.album_messages_with_link.append(message)
                await asyncio.sleep(1)
                await self.clean_ambiguous_album_mode_messages()
            else:
                await self.remove_message_without_image(message)
                
            
                
    async def on_message(self, message):
        if self.mentionned(message):
            await self.process_mention(message)
            return
        await self.handle_album_mode(message)








configFile = sys.argv[1]

client = discord.Client()
config = configparser.ConfigParser()
config.read(configFile)
bot = Bot(config, client)
token = config.get("discord", "token")

@client.event
async def on_ready():
    await bot.greet_channels()


@client.event
async def on_message(message):
    await bot.on_message(message)

@client.event
async def on_message_edit(old, new):
    await bot.on_message(message)


import atexit
from signal import signal, SIGTERM
from sys import exit
def save_conf():
    with open(sys.argv[1], 'w') as configfile:
        config.write(configfile)
atexit.register(save_conf)
signal(SIGTERM, lambda signum, stack_frame: exit(1))

client.run(token)