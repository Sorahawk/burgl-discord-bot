import discord, random

from bot_functions import *
from discord.ext import tasks
from global_variables import *
from secret_variables import DISCORD_BOT_TOKEN
from helper_functions import remove_command_prefix


bot = discord.Client()

@bot.event
async def on_ready():
	print(f'{bot.user} is online.')

	channel = bot.get_channel(MAIN_CHANNEL_ID)
	await channel.send(f"{CUSTOM_EMOJIS['BURG.L']} B-B-BURG.L is online!")

	rotate_status.start()


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	lowered_content = message.content.lower() + ' '

	# help method
	if lowered_content.startswith(BOT_COMMAND_LIST['help_method']):
		await message.channel.send(HELP_MESSAGE)

	else:
		for function, command in BOT_COMMAND_LIST.items():
			if lowered_content.startswith(command):
				user_input = remove_command_prefix(message.content, command)

				if user_input == '':
					await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} Please provide input parameters.")
				else:
					await eval(function)(message, user_input)


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(seconds=600)
async def rotate_status():
	chosen_activity, activity_info = random.choice(list(ACTIVITY_STATUSES.items()))

	if activity_info[0] == 1:
		activity = discord.Streaming(name=chosen_activity, url=activity_info[1])
	else:
		activity = discord.Activity(type=activity_info[0], name=chosen_activity)
	
	await bot.change_presence(activity=activity)


bot.run(DISCORD_BOT_TOKEN)
