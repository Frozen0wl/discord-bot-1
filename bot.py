import discord
from discord.ext import commands

from datetime import datetime

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

import keep_alive

client = commands.Bot(command_prefix=";", help_command=None)

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


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name=";help || Stalking PolarBear4u#7025"))
    print(f"[{datetime.now()}] {client.user}: Connected")


keep_alive.keep_alive()
client.run("ODI1NDIzMTkzNjk0Nzk3ODM0.YF9tQA.x66Eqll-DRhs-6XUDDYH6m1fH4s")
