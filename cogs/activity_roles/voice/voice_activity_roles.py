import discord
from discord.ext import commands, tasks

import json
import os

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util

import time
import datetime

from cogs.cmds.custom_checks import not_in_blacklist, is_moderator

class VcActivityRoles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.editing_json = False
        self.loaded = False
        self.database_id = "60d2fce20a8eed87da7c9f79"
        self.sync_stats_json()
        self.upload_json_to_database.start()


    # commands -----------------------------------------------------------------------
    @commands.command()
    @commands.guild_only()
    @commands.check(not_in_blacklist)
    async def vcstats(self, ctx, member: discord.Member = None):
        user = member
        if user is None:
            user = ctx.author

        embed = discord.Embed(title = f"User VC Stats [{str(user)} || {str(user.id)}]", color = discord.Color.orange())

        vcat_hours, vcat_minutes, vcat_seconds = self.seconds_to_hours_minutes_seconds(self.user_all_time(str(ctx.guild.id), str(user.id)))
        vcatg_hours, vcatg_minutes, vcatg_seconds = self.seconds_to_hours_minutes_seconds(self.user_all_time_global(str(user.id)))
        vcat_hours_14, vcat_minutes_14, vcat_seconds_14 = self.seconds_to_hours_minutes_seconds(self.user(str(ctx.guild.id), str(user.id), 14))
        vcatg_hours_14, vcatg_minutes_14, vcatg_seconds_14 = self.seconds_to_hours_minutes_seconds(self.user_global(str(user.id), 14))

        fields = [(f"VC All Time [{ctx.guild}]", f"{vcat_hours} hour(s), {vcat_minutes} minute(s), {vcat_seconds} second(s)", False),
                  ("VC All Time [Global]", f"{vcatg_hours} hour(s), {vcatg_minutes} minute(s), {vcatg_seconds} second(s)", False),
                  (f"VC last 14 days [{ctx.guild}]", f"{vcat_hours_14} hour(s), {vcat_minutes_14} minute(s), {vcat_seconds_14} second(s)", False),
                  ("VC last 14 days [Global]", f"{vcatg_hours_14} hour(s), {vcatg_minutes_14} minute(s), {vcatg_seconds_14} second(s)", False),
                  (f"VC Joins All Time [{ctx.guild}]", str(self.user_all_time_joins(str(ctx.guild.id), str(user.id))), False),
                  (f"VC Leaves All Time [{ctx.guild}]", str(self.user_all_time_leaves(str(ctx.guild.id), str(user.id))), False),
                  (f"VC Joins last 14 days [{ctx.guild}]", str(self.user_joins(str(ctx.guild.id), str(user.id), 14)), False),
                  (f"VC Leaves last 14 days [{ctx.guild}]", str(self.user_leaves(str(ctx.guild.id), str(user.id), 14)), False),
                  ("VC Joins All Time [Global]", str(self.user_all_time_joins_global(str(user.id))), False),
                  ("VC Leaves All Time [Global]", str(self.user_all_time_leaves_global(str(user.id))), False),
                  ("VC Joins last 14 days [Global]", str(self.user_joins_global(str(user.id), 14)), False),
                  ("VC Leaves last 14 days [Global]", str(self.user_leaves_global(str(user.id), 14)), False)
                  ]

        for name, value, inline in fields:
            embed.add_field(name = name, value = value, inline = inline)

        embed.set_footer(text=f"saving stats when user leaves vc")

        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.check(not_in_blacklist)
    async def vctop(self, ctx, lookback_days: int = 0): 
        toplist = list()
        title = ""

        if lookback_days <= 0:
            toplist = self.user_all_time_top(str(ctx.guild.id), 10)
            title = f"VC User Top [{ctx.guild}]"
        else:
            toplist = self.user_top(str(ctx.guild.id), 10, lookback_days)
            title = f"VC User Top [{ctx.guild}] [Last {lookback_days} days]"    

        embed = discord.Embed(title = title, color = discord.Color.orange())    

        count = 1
        for ti, userid in toplist:
            user = await self.client.fetch_user(userid)
            hours, minutes, seconds = self.seconds_to_hours_minutes_seconds(ti)

            cap = f"[{count}] {user}"
            count += 1

            embed.add_field(name=cap, value=f"{hours} hour(s), {minutes} minute(s), {seconds} second(s)", inline=False)

        embed.set_footer(text=f"saving stats when user leaves vc")

        await ctx.send(embed = embed)


    @commands.command()
    @commands.check(not_in_blacklist)
    async def vctopglobal(self, ctx, lookback_days: int = 0): 
        toplist = list()
        title = ""

        if lookback_days <= 0:
            toplist = self.user_all_time_global_top(10)
            title = f"VC User Top [Global]"
        else:
            toplist = self.user_global_top(10, lookback_days)
            title = f"VC User Top [Global] [Last {lookback_days} days]"  

        embed = discord.Embed(title = title, color = discord.Color.orange())

        count = 1
        for ti, userid in toplist:
            user = await self.client.fetch_user(userid)
            hours, minutes, seconds = self.seconds_to_hours_minutes_seconds(ti)

            cap = f"[{count}] {user}"
            count += 1

            embed.add_field(name=cap, value=f"{hours} hour(s), {minutes} minute(s), {seconds} second(s)", inline=False)

        embed.set_footer(text=f"saving stats when user leaves vc")

        await ctx.send(embed = embed)

    @commands.command()
    @commands.check(not_in_blacklist)
    async def vctopserver(self, ctx, lookback_days: int = 0): 
        toplist = list()
        title = ""

        if lookback_days <= 0:
            toplist = self.server_all_time_top(10)
            title = f"VC Server Top"
        else:
            toplist = self.server_top(10, lookback_days)
            title = f"VC Server Top [Last {lookback_days} days]" 

        embed = discord.Embed(title = title, color = discord.Color.orange()) 

        count = 1
        for ti, serverid in toplist:
            server = self.client.get_guild(int(serverid))
            hours, minutes, seconds = self.seconds_to_hours_minutes_seconds(ti)

            cap = f"[{count}] {server}"
            count += 1

            embed.add_field(name=cap, value=f"{hours} hour(s), {minutes} minute(s), {seconds} second(s)", inline=False)

        embed.set_footer(text=f"saving stats when user leaves vc")

        await ctx.send(embed = embed)

    @commands.command()
    @commands.check(not_in_blacklist)
    @commands.check(is_moderator)
    async def vcsj(self, ctx): # vc stats as a json file
        with open("user_voice_stats.json", "r") as file:
            await ctx.send("VC Stats JSON:", file=discord.File(file, "user_voice_stats.json"))

    
    # utils ------------------------------------------------------------------------
    def user_all_time(self, serverid: str, userid: str) -> float: # returns all time vc stats of user in seconds
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0.0
            elif userid not in stats[serverid]:
                return 0.0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0.0
            else:
                res = 0.0
                for i in stats[serverid][userid]["jlvc"]:
                    if len(i) != 2:
                        pass
                    else:
                        res += i[1] - i[0]
                return res

    def user(self, serverid: str, userid: str, lookback_days: int) -> float: # returns the stats of the last lookback_days days of an user in seconds
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0.0
            elif userid not in stats[serverid]:
                return 0.0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0.0
            else:
                res = 0.0
                for i in reversed(stats[serverid][userid]["jlvc"]):
                    if len(i) != 2:
                        pass
                    else:
                        if i[1] <= diff:
                            return res
                        elif i[0] < diff:
                            res += i[1] - diff
                            return res
                        else:
                            res += i[1] - i[0]
                return res
    
    def user_all_time_global(self, userid: str) -> float: # returns the sum of all time vc stats of user in all servers in seconds
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0.0
            else:
                res = 0.0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in stats[server][user]["jlvc"]:
                                        if len(i) != 2:
                                            pass
                                        else:
                                            res += i[1] - i[0]
                return res

    def user_global(self, userid: str, lookback_days: int) -> float: # returns the sum of all user vc stats in all servers of the last lookback_days days in seconds
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0.0
            else:
                res = 0.0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in reversed(stats[server][user]["jlvc"]):
                                        if len(i) != 2:
                                            pass
                                        else:
                                            if i[1] <= diff:
                                                break
                                            elif i[0] < diff:
                                                res += i[1] - diff
                                                break
                                            else:
                                                res += i[1] - i[0]
                return res

    def user_all_time_top(self, serverid: str, quan: int = 0) -> list: # returns top quan vc stats users of a specific server
        res = list()
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats: # no servers
                return []
            elif not stats[serverid]: # no members in server
                return []
            else:
                for member in stats[serverid]:
                    res.append([self.user_all_time(serverid, member), member])
        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]

    def user_top(self, serverid: str, quan: int = 0, lookback_days: int = 14) -> list: # returns top quan vc stats users of a specific server of the last lookback_days days
        res = list()
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats: # no servers
                return []
            elif not stats[serverid]: # no members in server
                return []
            else:
                for member in stats[serverid]:
                    res.append([self.user(serverid, member, lookback_days), member])
        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]
    
    def user_all_time_global_top(self, quan: int = 0) -> list: # returns top quan vc stats users (global) (bots included)
        users = list()
        res = list()

        # collect all users
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return []
            else:
                for server in stats:
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            users.append(user)

        for user in set(users):
            res.append([self.user_all_time_global(user), user])

        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]

    def user_global_top(self, quan: int = 0, lookback_days: int = 14) -> list: # returns top quan vc stats users (global) (bots included) of the last lookback_days days
        users = list()
        res = list()

        # collect all users
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return []
            else:
                for server in stats:
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            users.append(user)

        for user in set(users):
            res.append([self.user_global(user, lookback_days), user])

        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]

    def server_all_time_top(self, quan: int = 0) -> list: # returns top quan vc stats servers (global) (bots included in calculation)
        res = list()
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return []
            for server in stats:
                res.append([self.sum_user_all_time(server), server])
        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]

    def server_top(self, quan: int = 0, lookback_days: int = 14) -> list: # returns top quan vc stats servers (global) (bots inclued in calculation) of the last lookback_days days
        res = list()
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return []
            for server in stats:
                res.append([self.sum_user(server, lookback_days), server])
        if quan == 0:
            return sorted(res, reverse=True)
        return sorted(res, reverse=True)[:quan]

    def sum_user_all_time(self, serverid: str) -> float: # returns the sum of vc stats of all user of a specific server
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0.0
            elif serverid not in stats:
                return 0.0
            elif not stats[serverid]: # no members in server
                return 0.0
            else:
                res = 0.0
                for member in stats[serverid]:
                    res += self.user_all_time(serverid, member)
                return res
    
    def sum_user(self, serverid: str, lookback_days: int = 14) -> float: # returns the sum of vc stats of all user of a specific server of the last lookback_days days
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0.0
            elif serverid not in stats:
                return 0.0
            elif not stats[serverid]: # no members in server
                return 0.0
            else:
                res = 0.0
                for member in stats[serverid]:
                    res += self.user(serverid, member, lookback_days)
                return res
                    

    def user_all_time_joins(self, serverid: str, userid: str) -> int: # returns all time vc user joins
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0
            elif userid not in stats[serverid]:
                return 0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0
            else:
                res = 0
                for i in stats[serverid][userid]["jlvc"]:
                    if len(i) == 1 or len(i) == 2:
                        res += 1
                return res

    def user_joins(self, serverid: str, userid: str, lookback_days: int = 14) -> int: # returns vc user joins of the last lookback_days days
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0
            elif userid not in stats[serverid]:
                return 0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0
            else:
                res = 0
                for i in reversed(stats[serverid][userid]["jlvc"]):
                    if len(i) == 1 or len(i) == 2:
                        if i[0] < diff:
                            return res
                        res += 1
                return res

    def user_all_time_joins_global(self, userid: str) -> int: # returns all time vc user joins global (all servers)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0
            else:
                res = 0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in stats[server][user]["jlvc"]:
                                        if len(i) == 1 or len(i) == 2:
                                            res += 1
                return res

    def user_joins_global(self, userid: str, lookback_days: int = 14) -> int: # returns all time vc user joins global (all servers) of the last lookback_days days
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0
            else:
                res = 0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in reversed(stats[server][user]["jlvc"]):
                                        if len(i) == 1 or len(i) == 2:
                                            if i[0] < diff:
                                                break
                                            res += 1
                return res

    def user_all_time_leaves(self, serverid: str, userid: str) -> int: # returns all time vc user leaves
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0
            elif userid not in stats[serverid]:
                return 0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0
            else:
                res = 0
                for i in stats[serverid][userid]["jlvc"]:
                    if len(i) == 2:
                        res += 1
                return res

    def user_leaves(self, serverid: str, userid: str, lookback_days: int = 14) -> int: # returns vc user leaves of the last lookback_days days
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if serverid not in stats:
                return 0
            elif userid not in stats[serverid]:
                return 0
            elif len(stats[serverid][userid]["jlvc"]) == 0:
                return 0
            else:
                res = 0
                for i in reversed(stats[serverid][userid]["jlvc"]):
                    if len(i) == 2:
                        if i[1] < diff:
                            return res
                        res += 1
                return res

    def user_all_time_leaves_global(self, userid: str) -> int: # returns all time vc user leaves global (all servers)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0
            else:
                res = 0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in stats[server][user]["jlvc"]:
                                        if len(i) == 2:
                                            res += 1
                return res

    def user_leaves_global(self, userid: str, lookback_days: int = 14) -> int: # returns vc user leaves global (all servers) of the last lookback_days days
        diff = time.time() - (lookback_days * 24 * 60 * 60)
        with open("user_voice_stats.json", "r") as file:
            stats = json.loads(json.load(file))
            if not stats: # no servers
                return 0
            else:
                res = 0
                for server in stats: 
                    if len(stats[server]) == 0: # no members in server
                        pass
                    else:
                        for user in stats[server]:
                            if user == userid:
                                if len(stats[server][user]["jlvc"]) == 0: # user has no stats
                                    break
                                else:
                                    for i in reversed(stats[server][user]["jlvc"]):
                                        if len(i) == 2:
                                            if i[1] < diff:
                                                break
                                            res += 1
                return res
    
    def seconds_to_hours_minutes_seconds(self, seconds: float):
        ti = seconds
        hours = int(seconds // (60**2))
        ti -= hours*60**2
        minutes = int(ti // 60)
        ti -= minutes*60
        c_seconds = int(ti)
        return hours, minutes, c_seconds

    # syncing and collecting vc stats -----------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):    
        stats = None
        self.editing_json = True
        with open("user_voice_stats.json", "r") as file: # loading existing stats
            stats = json.loads(json.load(file))
        with open("user_voice_stats.json", "w") as file: # writing new stats
            if stats is None:
                stats = dict()
            if before.channel is None and after.channel is not None: # user joining vc
                stats = self.update_stats_json_join(stats.copy(), member)
            elif before.channel is not None and after.channel is None: # user leaving vc
                stats = self.update_stats_json_leave(stats.copy(), member)
            json.dump(json_util.dumps(stats), file)
        self.editing_json = False

    @tasks.loop(seconds=300) # every 5 minutes
    async def upload_json_to_database(self):
        if not self.loaded: 
            pass
        else:
            db_client = MongoClient(os.environ['MONGODB'])
            with db_client:
                db = db_client["activity"]
                stats_collection = db["user_voice"]
                stats = stats_collection.find_one(
                    ObjectId(self.database_id))
                with open("user_voice_stats.json", "r") as file:
                    json_stats = json.loads(json.load(file))
                    stats["data"] = json_stats
                stats_collection.update_one({"_id": ObjectId(self.database_id)}, {"$set": stats}, upsert=True)
        self.sync_stats_json()
            


    def update_stats_json_join(self, dic, member) -> dict:
        if str(member.guild.id) not in dic: # new server
            dic[str(member.guild.id)] = {str(member.id) : {"jlvc" : [[time.time()]]}}
            return dic
        elif str(member.id) not in dic[str(member.guild.id)]: # new member
            dic[str(member.guild.id)][str(member.id)] = {"jlvc" : [[time.time()]]}
        else:
            if len(dic[str(member.guild.id)][str(member.id)]["jlvc"][-1]) <= 1: # one or less time stamp
                dic[str(member.guild.id)][str(member.id)]["jlvc"][-1] = [time.time()]
            elif len(dic[str(member.guild.id)][str(member.id)]["jlvc"][-1]) == 2:
                dic[str(member.guild.id)][str(member.id)]["jlvc"].append([time.time()])
            else:
                dic[str(member.guild.id)][str(member.id)]["jlvc"].pop(-1)
                dic[str(member.guild.id)][str(member.id)]["jlvc"].append([time.time()])
        return dic


    def update_stats_json_leave(self, dic, member) -> dict:
        if str(member.guild.id) not in dic: # new server --> do nothing
            return dic 
        elif str(member.id) not in dic[str(member.guild.id)]: # new member --> do nothing
            return dic
        else:
            if len(dic[str(member.guild.id)][str(member.id)]["jlvc"][-1]) == 0:
                return dic
            elif len(dic[str(member.guild.id)][str(member.id)]["jlvc"][-1]) == 1:
                dic[str(member.guild.id)][str(member.id)]["jlvc"][-1].append(time.time())
            else:
                return dic
        return dic

                      

    def sync_stats_json(self): 
        db_client = MongoClient(os.environ['MONGODB'])
        with db_client:
            db = db_client["activity"]
            stats_collection = db["user_voice"]
            stats = stats_collection.find_one(
                ObjectId(self.database_id))
            with open("user_voice_stats.json", "w") as file:
                json.dump(json_util.dumps(stats["data"]), file)
        self.loaded = True

            

    