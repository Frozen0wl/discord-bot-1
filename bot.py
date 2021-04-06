import discord
from discord.ext import commands, tasks

import os
from itertools import cycle

from datetime import datetime

from cogs.cmds.help_cmds import HelpCmds
from cogs.cmds.general_cmds import GeneralCmds
from cogs.cmds.testing_cmds import TestingCmds
from cogs.cmds.vc_cmds import VcCmds
from cogs.cmds.fun_cmds import FunCmds
from cogs.cmds.math_cmds import MathCmds
from cogs.cmds.dumb_cmds import DumbCmds
from cogs.cmds.management_cmds import ManagementCmds

from cogs.non_cmds.troll_flori import TrollFlori
from cogs.non_cmds.events import Events

from cogs.activity_roles.voice.voice_activity_roles import VcActivityRoles

client = commands.Bot(command_prefix=";", help_command=None)

client.add_cog(HelpCmds(client))
client.add_cog(GeneralCmds(client))
client.add_cog(TestingCmds(client))
client.add_cog(VcCmds(client))
client.add_cog(FunCmds(client))
client.add_cog(MathCmds(client))
client.add_cog(DumbCmds(client))
client.add_cog(ManagementCmds(client))

client.add_cog(TrollFlori(client))
client.add_cog(Events(client))

client.add_cog(VcActivityRoles(client))

bot_status = cycle([f";help || Stalking {os.environ['MY_DISCORD_TAG']}", "Watching Overlord", f"bot host started at: {datetime.now()}"])

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb)
    change_status.start()
    print(f"[{datetime.now()}] {client.user}: Connected")

@tasks.loop(seconds = 10)
async def change_status():
    await client.change_presence(activity = discord.Game(name = next(bot_status)))

client.run(os.environ['BOT_TOKEN'])


