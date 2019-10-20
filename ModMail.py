import os
import discord
import datetime

client = discord.Client()
adminRole = 635572718208548864
closeChannel = "!close"
currentChannels = {1:1}

@client.event
async def on_ready():
	print(client.guilds[0].name)
	await client.change_presence(activity=discord.Activity(name="DM to contact Mods", type=3))
	category = await create_category(client.guilds[0])
	for chan in category.channels:
		await chan.delete()
	await category.delete()
	category = await create_category(client.guilds[0])
	await category.create_text_channel("ModMail Logs")

@client.event
async def on_member_join(member):
	await member.send("**Welcome to the /r/LegendsOfRuneterra Discord server!**\n\nBefore you get started chatting, take a second to look through the <#633713480440086550> and <#633885495360749568> to get set up within the server.\n\nIf you have a question to ask, check out <#634171933725949952> first as it may have already been answered.\n\nIf you need help, reply directly to me - " + client.user.mention + " - and a team member will get back to you as soon as possible.")
	embed = discord.Embed(color=0x2c2f33, timestamp=datetime.datetime.utcnow())
	embed.set_image(url = "https://cdn.discordapp.com/attachments/634547576976310275/635242533877972993/logo.png")
	await member.send(embed=embed)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	
	category = await create_category(client.guilds[0])

	if isinstance(message.channel, discord.DMChannel):
		text_channel = await create_text_channel(category, message.author)

		if currentChannels.get(text_channel.id) == None:
			currentChannels.update({text_channel.id:message.author.id})
			await text_channel.send(client.guilds[0].get_role(adminRole).mention)
			await text_channel.send("**" + message.author.name + "#" + message.author.discriminator + " Requires your assistance with the following:**")
			await text_channel.send(message.content)
			await message.author.send("Your message has been received by the /r/LegendsOfRuneterra team!")
		else:
			await text_channel.send(message.content)
	elif message.channel.category_id == category.id:
		if message.content == closeChannel:
			await client.get_user(currentChannels[message.channel.id]).send("The /r/LegendsOfRuneterra team has marked your issue as resolved.")
			await log_conversation(await find_log_channel(category), await message.channel.history(limit=100).flatten())
			del currentChannels[message.channel.id]
			await message.channel.delete()
		else:
			await client.get_user(currentChannels[message.channel.id]).send("**" + message.author.name + ":** " + message.content)


async def create_category(guild):
	for cat in guild.categories:
		if cat.name == "LoR ModMail":
			return cat
	overwrites = {
    	client.guilds[0].default_role: discord.PermissionOverwrite(read_messages=False),
    	client.guilds[0].get_role(adminRole): discord.PermissionOverwrite(read_messages=True)
	}
	return await guild.create_category("LoR ModMail", overwrites=overwrites)

async def create_text_channel(category, author):
	for channel in category.text_channels:
		if currentChannels.get(channel.id) == author.id:
			return channel
	return await category.create_text_channel(author.name + author.discriminator)

async def log_conversation(logChannel, history):
	history.reverse()
	for message in history:
		await logChannel.send("**" + message.author.name + ":** " + message.content)

async def find_log_channel(category):
	for channel in category.text_channels:
		if channel.name == "modmail-logs":
			return channel

client.run('bot_id')