# Slack to Discord archive import

Transfer Slack archives to a Discord server on a per-channel basis using a Discord bot.

### Prerequisites

1. The bot is a command-line utility written in Python 3, so you should be comfortable with using that.
2. The bot uses the Python library [discord.py](https://pypi.org/project/discord.py/). It can be installed easily by following the instruction at the library page.


### Create a Discord bot

The Internet is full of tutorials on how this is done, but briefly:

* Use [Applications at the Discord developer portal](https://discord.com/developers/applications) to create a new application. A good name for it is "Archive". It will appear as the sender of the messages transferred from Slack to Discord.
* In the application setting, turn it into a bot (the "Bot" tab in the left-hand menu)
* Under "OAuth2" settings, generate an invitation URL for your bot. Under "Scopes" select `bot` and
  `applications.commands` and then under "Bot permissions" `admin` (which is probably overkill). Visit the URL and
  invite the bot to your Discord server. If all goes well, the bot will appear on your Discord server (logged out).
* Under "Bot" settings, get the bot token, which you will need to authorize the script.

### Archive Slack

Follow [these instructions](https://slack.com/intl/en-si/help/articles/201658943-Export-your-workspace-data) to export your Slack data as a zip file. We assume that the extracted archive is placed in folder `⟨slack-archive⟩`. Observe that it contains, among other things:

* `users.json` -- a JSON file describing Slack users
* for each channel `#foo` a subfolder `foo` with many JSON files constituting the channel archive

### Usage

Each execution of the bot imports the contents of one channel. If you have many channels, repeat the process described here for each channel separately.

To transfer the archive for a Slack channel `#foo` to Discord channel `#foo`, proceed as follows.

1. Create the Discord channel `#foo` if you have not done so already.
2. When you run the bot from the command line, you have to provide:

   * the bot token, as described above, via the `--token` command-line argument
   * the location of the Slack `users.json` file, via the `--users` commmand-line argument
   * the list of JSON files holding the channel archive

   A typical invocation of the bot thus looks something like this:

   ```
   python3 ./slack2discord.py --token '⟨bot-token⟩' --users ⟨slack-archive⟩/users.json ⟨slack-archive⟩/foo/*.json
   ```

   Run `python3 ./slack2discord.py --help` for a description of available command-line arguments.

   If all goes well, the bot will process the archived messages and make itself ready for posting them to Discord.
   At this point, on the Discord server you should see the bot as logged in.

2. If you wish to preview the messages that will be imported, run the command `!slackpreview` in channel `#foo`.
   The bot will print the messages on the command line, but will not import them into Discord yet.

3. To start importing the archive into Discord channel `#foo`, issue the command `!slackimport` in channel `#foo`.
   Note that the process may take quite a bit of time since the bot must respect upload limitations set by Discord.
   On the command-line the bot will print out progress. If you want to abort, just press Ctrl-C.

4. To stop the bot, either press Ctrl-C on the command-line, or run the `!slackexit` command in channel `#foo`.

### Customization

It is fairly easy to tinker with the source code and customize the format of the messages posted to Discord. Have a look at the `slackimport` function, and in particular the call to `ctx.send`, which generates the message.

If there is sufficient interest, in the future we may provide customization options via the command line.

