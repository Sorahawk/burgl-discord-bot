from var_global import *
from storage_functions import *
from string_processing import *

from re import findall
from discord import DMChannel
from asyncio import TimeoutError


# returns True if message author is elevated, otherwise False
async def check_user_elevation(message, flag_presence):
	if flag_presence['override'] and message.author.id == SUPER_USER_ID:
		await burgl_message('authorisation_override', message)
		return True

	try:
		for role in message.author.roles:
			if role.id in ELEVATED_USER_ROLES:
				return True
	except:
		# the try block will fail in DMs because there are no roles
		pass

	return False


# inserts BURG.L emoji to front of specified voiceline and sends message to the given channel
# returns message object so that it can be edited by caller functions
async def burgl_message(key, message=None, replace=None, notify=False):
	voiceline = BOT_VOICELINES[key]

	if replace:  # insert custom string into voiceline
		voiceline = voiceline.replace('VAR1', f"'{replace}'")

	if notify:  # notify users
		voiceline = f"{NOTIFY_ROLE_NAME} {voiceline}"

	# append BURG.L emoji and italicise text content
	voiceline = prefix_burgl_emoji(voiceline)

	# send specific lines to main channel also so that real-time bot status is reflected
	if not message or (key in ['hello', 'sleeping', 'debug', 'cleared'] and message.channel != var_global.MAIN_CHANNEL):
		await var_global.MAIN_CHANNEL.send(voiceline)

	if message:
		return await message.channel.send(voiceline)


# display corresponding error message if result is an error
# returns True if no error, else returns None by default
async def detect_errors(message, user_input, result):

	# catch specific error cases which return different data types, e.g. 102
	if isinstance(result, list) and isinstance(result[0], int):
		await burgl_message(result[0], message, replace=result[1])

	# check voiceline dictionary in var_global directly so no need to keep updating here too
	elif isinstance(result, int) and result in BOT_VOICELINES:
		full_name = custom_capitalise_string(retrieve_full_name(user_input))
		await burgl_message(result, message, replace=full_name)

	else:
		return True


# standard handler for multi-page messages, which allows for page navigation, as well as closing the menu
# unique input is embed_list, which is the list of discord.Embed messages to display, in page order
async def multipage_embed_handler(message, user_input, embed_list):
	if len(embed_list) == 0:
		return await burgl_message('no_display', message)
	
	current_page = 0
	direct_page = findall('\d+', user_input)

	# see if a valid page number was specified and navigate to it directly if so
	for number in direct_page:
		number = int(number)

		if number <= len(embed_list):
			current_page = number - 1
			break

	left_arrow = CUSTOM_EMOJIS['LeftArrow']
	cross_mark = CUSTOM_EMOJIS['CrossMark']
	right_arrow = CUSTOM_EMOJIS['RightArrow']

	embedded_message = await message.channel.send(embed=embed_list[current_page])

	await embedded_message.add_reaction(left_arrow)
	await embedded_message.add_reaction(cross_mark)
	await embedded_message.add_reaction(right_arrow)


	# returns True if emoji reaction by user to the specific embed message is one of the specified emojis
	def multipage_emoji_check(reaction, user):
		return user != var_global.BOT_INSTANCE.user and reaction.message.id == embedded_message.id and reaction.emoji in [left_arrow, cross_mark, right_arrow]


	while True:
		try:
			reaction, user = await var_global.BOT_INSTANCE.wait_for('reaction_add', timeout=60, check=multipage_emoji_check)

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

			except:  # MessageNotFound errors, which can happen if the message is deleted before timeout occurs
				pass
