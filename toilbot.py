# toilbot.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import random
import asyncio
import time
from collections import OrderedDict

########## CONSTANTS

load_dotenv()
TOKEN = os.getenv('TOILBOT_TOKEN')

BOT_OWNER = 205908835435544577;

moons = [":full_moon:", ":waxing_gibbous_moon:", ":first_quarter_moon:", ":waxing_crescent_moon:", ":new_moon:", 
		 ":waning_crescent_moon:", ":last_quarter_moon:", ":waning_gibbous_moon:", ":full_moon:"]

#mixtea
freq_thresh = 500

emoji_first_place = "🥇"
emoji_second_place = "🥈"
emoji_third_place = "🥉"
emoji_check_mark = "✅"

########## END CONSTANTS
########## GLOBALS

teaGame = None #will hold the Tea object
teaMode = "none"
teaPrompts = {
	"long":  "Type the longest word containing: ",
	"quick": "Quickly type a word containing: ",
	"many":  "Type as many words as possible containing: "
}

########## END GLOBALS

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
	print(f'{bot.user} has connect to Discord!')

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	global teaGame
	if teaMode != "none" and message.channel == teaGame.ctx.channel:
		if teaMode == "long":
			wordStatus = teaGame.submitWord(message.content, message.author)
			if wordStatus == 2:
				await message.add_reaction(emoji_first_place)
			elif wordStatus == 1:
				await message.add_reaction(emoji_check_mark)
		elif teaMode == "quick":
			print("quick")
		elif teaMode == "many":
			print("many")

	await bot.process_commands(message)


class Tea:

	def __init__(self, ctx):
		self.ctx = ctx
		self.rawWords = open("collins_scrabble.txt", "r").read()
		self.wordsList = self.rawWords.split("\n")
		self.phrase = ""
		self.randWord = ""
		self.timeCounter = 0
		self.roundOver = 0
		self.scores = {}
		self.usedWords = []
#		self.startGame() #has to be called manually outside the class since it has to be awaited

	async def startGame(self):
		self.generateWord()
		self.timer(teaPrompts["long"] + "**" + self.phrase + "**")
		global teaMode
		teaMode = "long"
		await asyncio.sleep(10)

		self.roundOver = 1
		teaMode = "none"

		sortedScores = sorted(self.scores.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
		for i in sortedScores:
			if i[1] == 0:
				sortedScores.remove(i)

		if len(sortedScores) == 0:
			await self.ctx.send(f"Nobody wins the round. A word that would've been accepted is **{self.randWord}**.")
		else:
			winOutput = ""
			i = 0
			for score in sortedScores:
				if i == 0:
					winOutput += ":first_place: "
				elif i == 1:
					winOutput += ":second_place: "
				elif i == 2:
					winOutput += ":third_place: "
				else:
					winOutput += ":medal "
				winOutput += score[0].mention + " wins " + str(score[1]) + " points.\n" #TODO point scaling
				i += 1

			await self.ctx.send(winOutput)

#	def submitWord(self, word, user): #overridden by subclasses


	def generateWord(self):
		belowThreshold = 1
		while belowThreshold == 1:
			randWord = self.wordsList[random.randint(0, len(self.wordsList)-1)]
			randIndex = random.randint(0, len(randWord)-3)
			phrase = randWord[randIndex:randIndex+3]
			frequency = self.rawWords.count(phrase)
			if (frequency > freq_thresh): #make sure phrase appears enough times
				self.phrase = phrase
				self.randWord = randWord
				belowThreshold = 0
#			print(f"word: {randWord}\nindex: {randIndex}\nphrase: {phrase}\nfrequency: {frequency}")

	def timer(self, startMsg):
		async def background_counter(ctx):
			await bot.wait_until_ready()
			counterMessage = None
			global moons
			while not bot.is_closed():
				if self.timeCounter == 9: #timer is done
					return
				elif self.timeCounter == 0: #start timer
					await ctx.send(startMsg)
					counterMessage = await ctx.send(moons[self.timeCounter])
				else: #update timer
					await counterMessage.edit(content=moons[self.timeCounter])
				await asyncio.sleep(1)
				self.timeCounter += 1
		bot.loop.create_task(background_counter(self.ctx))

class LongTea(Tea):

	def __init__(self, ctx):
		super().__init__(self, ctx)
		self.longestWord = ""

	def submitWord(self, word, user):
		if user not in self.scores:
			self.scores[user] = 0
		if self.phrase.lower() in word.lower() and word.lower() not in self.usedWords and len(word) > self.scores[user]:
			if word.upper() in self.wordsList: 
				self.usedWords.append(word.lower())
				self.scores[user] = len(word)
				longestUser = max(self.scores, key=self.scores.get)
				if longestUser == user:
					self.longestWord = word.upper()
					return 2 #longest word for all
				else:
					return 1 #longest word for user
			else:
				return 0 #invalid word


class QuickTea(Tea):
	pass

class ManyTea(Tea):
	pass


@bot.command(aliases=["tt"])
async def teatest(ctx):
	global teaGame
	teaGame = Tea(ctx)
	await teaGame.startGame()


@bot.command()
async def dict(ctx):
	scores = {}
	scores["ptoil"] = 5
	scores["gumies"] = 0
	scores["pans"] = 8

	sortedScores = sorted(scores.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)

	for i in sortedScores:
		if i[1] == 0:
			sortedScores.remove(i)

	output = ""
	for score in sortedScores:
		output += score[0] + ": " + str(score[1]) + "\n"	
	await ctx.send(output)




@bot.command(aliases=["moontea"])
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
async def say(ctx, botName: str, *strInput: str):
	if ctx.author.id == BOT_OWNER:
		if (botName == "toilbot"):
			await ctx.send(" ".join(strInput))
	else:
		await ctx.send(f"{ctx.author.mention} You don't have permission to use that command.")

@bot.command()
async def dodrop(ctx):
	await ctx.send(".drop")

@bot.command()
async def accountage(ctx):
	await ctx.send(f"{ctx.author.mention}'s account was made on {ctx.author.created_at}")

@bot.command()
async def shutdown(ctx, botName: str):
	if ctx.author.id == BOT_OWNER:
		if botName == "toilbot":
			await ctx.send("Shutting down")
			print("Bot was shutdown")
			await bot.logout()
	else:
		await ctx.send("You don't have permission to use that command.")

bot.run(TOKEN)