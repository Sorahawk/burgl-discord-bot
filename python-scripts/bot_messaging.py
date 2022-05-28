from discord import DMChannel
from asyncio import TimeoutError

from global_variables import *
from string_processing import *


# inserts BURG.L emoji to front of specified voiceline and sends message to the given channel
async def burgl_message(key, message=None):
	voiceline = prefix_burgl_emoji(BOT_VOICELINES[key])

	if message:
		await message.channel.send(voiceline)

	# send specific lines to main channel also so that real-time bot status is reflected
	if not message or (key in ['hello', 'sleeping', 'debug', 'cleared'] and message.channel != global_variables.MAIN_CHANNEL):
		await global_variables.MAIN_CHANNEL.send(voiceline)


# standard handler for multi-page messages, which allows for page navigation, as well as closing the menu
# unique input is embed_list, which is the list of discord.Embed messages to display, in page order
async def multipage_embed_handler(bot, message, embed_list):
	if len(embed_list) == 0:
		return await burgl_message('no_bindings', message)

	left_arrow = CUSTOM_EMOJIS['LeftArrow']
	cross_mark = CUSTOM_EMOJIS['CrossMark']
	right_arrow = CUSTOM_EMOJIS['RightArrow']

	current_page = 0
	embedded_message = await message.channel.send(embed=embed_list[current_page])

	await embedded_message.add_reaction(left_arrow)
	await embedded_message.add_reaction(cross_mark)
	await embedded_message.add_reaction(right_arrow)


	# returns True if emoji reaction by user to the specific embed message is one of the specified emojis
	def multipage_emoji_check(reaction, user):
		return user != bot.user and reaction.message.id == embedded_message.id and reaction.emoji in [left_arrow, cross_mark, right_arrow]


	while True:
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=60, check=multipage_emoji_check)

			if reaction.emoji == cross_mark:
				if isinstance(message.channel, DMChannel):  # check if channel is a private chat
					return await embedded_message.delete()

				else:
					await embedded_message.clear_reactions()
					return await embedded_message.edit(content=prefix_burgl_emoji(BOT_VOICELINES['embed_close']), embed=None)

			elif reaction.emoji == left_arrow:
				if current_page == 0:
					# wrap-around to the end
					current_page = len(embed_list) - 1
				else:
					current_page -= 1

			elif reaction.emoji == right_arrow:
				if current_page == len(embed_list) - 1:
					# wrap-around to the start
					current_page = 0
				else:
					current_page += 1

			await embedded_message.edit(embed=embed_list[current_page])

			if not isinstance(message.channel, DMChannel):
				await embedded_message.remove_reaction(reaction, user)

		except TimeoutError:
			try:
				# after specified timeout period, remove 'buttons' from the message
				# leaves the info on screen, but also informs the user that pages can no longer be navigated
				return await embedded_message.clear_reactions()

			except:  # other errors, like discord.errors.NotFound: Unknown Message (if message is deleted)
				return
