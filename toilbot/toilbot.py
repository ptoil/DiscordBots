import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import traceback
from cogs.exceptions import *

import random
import asyncio
import time
import logging

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv('TOILBOT_TOKEN')


#logging.basicConfig(level=logging.INFO)

BOT_OWNER = 205908835435544577


moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
		 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]


########## END CONSTANTS

intents = discord.Intents(messages=True, members=True, guilds=True, reactions=True, voice_states=True, message_content=True)
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)


bot.load_extension("cogs.mixtea", store=False)
bot.load_extension("cogs.connectfour", store=False)
#bot.load_extension("cogs.blackjack", store=False)
bot.load_extension("cogs.roles", store=False)
bot.load_extension("cogs.cobecog", store=False)
#bot.load_extension("cogs.cubing", store=False)
bot.load_extension("cogs.voice", store=False)

@bot.event
async def on_connect():
	bot.printDebugMessages = False
	print(f'{bot.user} has connected to Discord')

@bot.event
async def on_ready():
	print(f'{bot.user} is ready!')

@bot.command()
@commands.is_owner()
async def toggledebug(ctx):
	bot.printDebugMessages = not bot.printDebugMessages
	if bot.printDebugMessages:
		await ctx.send("Debug is ON")
	else:
		await ctx.send("Debug is OFF")

@bot.event
async def on_command_error(ctx, error):
	errorsHandledLocally = (commands.MissingRequiredArgument, commands.MemberNotFound)
	customErrors = (NotInToilbotChannel, NotInToilbotOrCubingChannel, NotOwnerOrGuildOwner, NotInToilbotsVC)

	if isinstance(error, commands.errors.CommandNotFound):
		pass
	elif isinstance(error, commands.errors.NotOwner):
		await ctx.send("Only ptoil has access to that command <:FUNgineer:918637730542522408>")
	elif isinstance(error, errorsHandledLocally):
		pass #handled locally per command
	elif isinstance(error, customErrors):
		print(f"{error.name}: {ctx.author.name}: {ctx.message.content}")
	elif isinstance(error, commands.errors.CheckFailure):
		pass #If the check failed then I wanted it to be ignored
	else:
		print('Ignoring exception in command {}:'.format(ctx.command))
		print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
		await ctx.send(f"<@205908835435544577> pepew\n{type(error)}: {error}")


"""
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	await bot.process_commands(message)
"""


@bot.command(aliases=["moontea"])
@CustomChecks.in_toilbot_channel()
async def moon(ctx):
	counterMessage = None
	counter = 0
	global moons
	while not bot.is_closed():
		if counter == 0:
				counterMessage = await ctx.send(moons[counter])
		else:
			await counterMessage.edit(content=moons[counter])
		await asyncio.sleep(1)
		counter += 1
		if counter == 9:
			return;

@bot.command()
@CustomChecks.is_owner_or_guild_owner()
async def say(ctx, *strInput: str):
	await ctx.send(" ".join(strInput))
	await ctx.message.delete()

@bot.command()
@CustomChecks.in_toilbot_channel()
async def sourcecode(ctx):
	await ctx.send("https://github.com/ptoil/DiscordBots")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send("Shutting down")
	print("Bot was shutdown")
	await bot.close()

bot.run(TOKEN)
