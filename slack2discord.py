#!/usr/bin/env python3

import asyncio
import datetime
import discord
from discord.ext import commands
import json
import argparse
import sys
import re

arg_parser = argparse.ArgumentParser(description="A Discord bot for transferring a Slack archive to a channel")
arg_parser.add_argument('--prefix', dest='prefix', default='!', help='bot command prefix (default !)')
arg_parser.add_argument('--token', required=True, help='bot access token')
arg_parser.add_argument('--users', required=True, type=argparse.FileType('r'), help='slack users.json file')
arg_parser.add_argument('file', nargs='+', type=argparse.FileType('r'))

# Parse the command-line
args = arg_parser.parse_args(sys.argv[1:])

# Load user data
users = {}
for u in json.load(args.users):
    if not u['deleted']:
        users[u['id']] = u['real_name']

# Process the input files
messages = []
for fh in args.file:
    for msg in json.load(fh):
        txt = re.sub(r'<@(\w+)>',
                     (lambda m: '@' + users[m.group(1)]),
                     msg["text"])
        txt = re.sub(r'&gt;', '>', txt)
        txt = re.sub(r'&lt;', '<', txt)
        txt = re.sub(r'&amp;', '&', txt)

        # Split messages longer than 2000 characters
        while len(txt) > 0:
            msg["text"] = txt[:2000]
            txt = txt[2000:]
            messages.append(msg)

print("Read {0} messages.".format(len(messages)))

# Create the bot
bot = commands.Bot(command_prefix=args.prefix)

print("Activating the bot.")

# Set up the bot listener
@bot.command(pass_context=True)
async def slackimport(ctx):
    n = len(messages)
    k = 0
    print ("Sending {0} messages ...".format(n))
    for msg in messages:
        k = k + 1
        if k % 20 == 0: print ("{0}/{1} messages sent ...".format(k, n))
        try:
            await ctx.send ("{timestamp} {user}: {text}".format(
                timestamp = datetime.datetime.fromtimestamp(float(msg['ts'])).strftime('%Y-%m-%d %H:%M'),
                user=users[msg['user']],
                text=msg['text']))
        except:
            print("Message {0} could not be sent.".format(k))
    print ("Sent!")


@bot.command(pass_context=True)
async def slackexit(ctx):
    print("Stopping.")
    await bot.logout()
    exit(0)

# Run the bot
bot.run(args.token)
