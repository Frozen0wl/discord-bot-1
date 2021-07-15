import discord
from discord.ext import commands

import os

from pymongo import MongoClient
from bson.objectid import ObjectId

import json

import random

from cogs.cmds.custom_checks import is_moderator, not_in_blacklist

class FunCmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def right(self, ctx):
        k = random(0, 1)
        if is_moderator():
            await ctx.send(f"Yes {ctx.author.name}, you are right!")
        elif k == 0:
            await ctx.send(f"No screw you!")
        else:
            await ctx.send(f"Absolutely")


    @commands.command()
    @commands.check(not_in_blacklist)
    async def quote(self, ctx):
        with open("./cogs/cmds/cmd_utils/quotes.json", "r") as file:
            quotes = json.load(file)
            ind = random.randint(0, len(quotes) - 1)
            await ctx.send(quotes[ind])

    @commands.command()
    @commands.check(not_in_blacklist)
    async def morse(self, ctx, *sentence):
        with open("./cogs/cmds/cmd_utils/morse_code_dict.json", "r") as file:
            MORSE_CODE_DICT = json.load(file)
            res = ""
            for word in sentence:
                for char in word:
                    res += MORSE_CODE_DICT[char.upper()]
                    res += " "

            await ctx.send(res)

    @commands.command()
    @commands.check(not_in_blacklist)
    async def demorse(self, ctx, *sentence):
        with open("./cogs/cmds/cmd_utils/morse_code_dict.json", "r") as file:
            MORSE_CODE_DICT = json.load(file)
            div = dict()
            for key, value in MORSE_CODE_DICT.items():
                div[value] = key

            res = ""
            for mchar in sentence:
                res += div[mchar].lower()

            await ctx.send(res)

    @commands.command()
    @commands.check(not_in_blacklist)
    async def ascii(self, ctx, *sentence):
        res = ""
        for word in sentence:
            for char in word:
                res += str(ord(char))
                res += "/"
            res = res[:-1]
            res += " | "
        res = res[:-3]
        await ctx.send(res)

    @commands.command()
    @commands.check(not_in_blacklist)
    async def ranimegif(self, ctx):
        with open("./cogs/cmds/cmd_utils/anime_gifs.json", "r") as file:
            anime_gifs = json.load(file)
            await ctx.send(anime_gifs[random.randint(0, len(anime_gifs) - 1)])

    @commands.command()
    @commands.check(not_in_blacklist)
    async def note(self, ctx, *, n : str = None):
        obj_id = "607f305065c78e14e94bf714"
        data = dict()
        client = MongoClient(os.environ['MONGODB'])
        with client:
            db = client["fun_cmds"]
            notes_collection = db["note"]
            if notes_collection.find_one(ObjectId(obj_id)) is not None:
                data = notes_collection.find_one(ObjectId(obj_id))

            if n is None:
                data[str(ctx.author.id)] = "UwU"
            else:
                data[str(ctx.author.id)] = n
                
            notes_collection.update_one({"_id":ObjectId(obj_id)}, {"$set": data}, upsert = True)

            await ctx.send("saved changes")

    @commands.command()
    @commands.check(not_in_blacklist)
    async def rnote(self, ctx):
        obj_id = "607f305065c78e14e94bf714"
        data = dict()
        client = MongoClient(os.environ['MONGODB'])
        with client:
            db = client["fun_cmds"]
            notes_collection = db["note"]
            if notes_collection.find_one(ObjectId(obj_id)) is not None:
                data = notes_collection.find_one(ObjectId(obj_id))

            if str(ctx.author.id) not in data:
                await ctx.send(f"do not have a note. please create a note with {self.client.command_prefix(self.client, ctx)}note")
            else:
                await ctx.send(data[str(ctx.author.id)])

