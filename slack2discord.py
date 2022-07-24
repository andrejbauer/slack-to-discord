#!/usr/bin/env python3

import discord
from discord.ext import commands
import datetime
import json
import argparse
import sys
import re

arg_parser = argparse.ArgumentParser(description="A Discord bot for transferring a Slack archive to a channel")
arg_parser.add_argument('--prefix', dest='prefix', default='!', help='bot command prefix (default !)')
arg_parser.add_argument('--token', required=True, help='bot access token')
arg_parser.add_argument('--users', required=True, type=argparse.FileType('r'), help='slack users.json file')
arg_parser.add_argument('file', nargs='+')

# Parse the command-line
args = arg_parser.parse_args(sys.argv[1:])

# Load user data
users = {}
for u in json.load(args.users):
    if not u['deleted']:
        users[u['id']] = u['real_name']

# Process the input files
messages = []
for fn in args.file:
    with open(fn, "rb") as fh:
        for msg in json.load(fh):
            # Unfold mentions
            txt = re.sub(r'<@(\w+)>',
                         (lambda m: '@' + users.get(m.group(1), 'Unknown')),
                         msg["text"])
            # Unescape HTML characters
            txt = re.sub(r'&gt;', '>', txt)
            txt = re.sub(r'&lt;', '<', txt)
            txt = re.sub(r'&amp;', '&', txt)

            # Split messages longer than 2000 characters
            while len(txt) > 0:
                msg["text"] = txt[:2000]
                txt = txt[2000:]
                messages.append(msg)

# Sort the messages by timestamp
messages.sort(key=(lambda msg: msg['ts']))

print("Read {0} messages.".format(len(messages)))

# Create the bot
bot = commands.Bot(command_prefix=args.prefix)

print("Activating the bot. Press Ctrl-C to exit.")

def format_message(msg):
    """Format the given message in Markdown, suitable for posting on Discord."""
    if(msg.get('files')):
            url=msg.get('files')[0].get('url_private')
    else:
            url=""
    return "{timestamp} **{user}**: {text} {url}".format(
        timestamp = datetime.datetime.fromtimestamp(float(msg['ts'])).strftime('%Y-%m-%d %H:%M'),
        user='Unknown',
        text=msg['text'],
        url=url)

# Set up the bot listener
@bot.command(pass_context=True)
async def slackimport(ctx):
    n = len(messages)
    k = 0
    print ("Sending {0} messages ...".format(n))
    for msg in messages:
        k = k + 1
        if k % 10 == 0: print ("{0}/{1} messages sent ...".format(k, n))
        try:
            # Send the message to Discord (Markdown format)
            await ctx.send (format_message(msg))
        except:
            print("Message {0} could not be sent.".format(k))
    print ("Finished sending messages. My job is done, kill me now.")


@bot.command(pass_context=True)
async def slackpreview(ctx):
    for msg in messages:
        print("-" * 50)
        print(format_message(msg))

@bot.command(pass_context=True)
async def slackexit(ctx):
    print("Logging out ...")
    await bot.logout()
    print("Stopping (do not worry about the error messages printed below) ...")
    exit(0)

# Run the bot
bot.run(args.token)
