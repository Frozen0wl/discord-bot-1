import discord
from discord.ext import commands

from cogs.cmds.custom_checks import is_moderator


class ManagementCmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["arole"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await ctx.send(f"Permission granted")
        await member.add_roles(role)
        await ctx.send(f"added {role} to {member}")

    @commands.command(aliases=["rrole"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remrole(self, ctx, member: discord.Member, role: discord.Role):
        await ctx.send(f"Permission granted")
        await member.remove_roles(role)
        await ctx.send(f"{role} removed from {member}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't kick yourself")
        else:
            await ctx.send(f"Permission granted")
            await member.kick(reason=reason)
            await ctx.send(f"Kicked {member}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't ban yourself")
        else:
            await ctx.send(f"Permission granted")
            await member.ban(reason=reason)
            await ctx.send(f"Banned {member}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unban(self, ctx, id: int):
        user = await self.client.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nick: str):
        await member.edit(nick=nick)
        await ctx.send(f"Nickname change: {member}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def nicknames(self, ctx, *, n : str = None):
        nick = None
        for user in ctx.guild.members:
            if n is None:
                nick = user.name
            else:
                nick = n
            try:
                await user.edit(nick=nick)
                await ctx.send(f"changed {user}'s nickname to: [{nick}]")
            except discord.errors.Forbidden:
                await ctx.send(f"do not have enough permissions to change {user}'s nickname")
        await ctx.send("changed all nicknames that could be changed")
