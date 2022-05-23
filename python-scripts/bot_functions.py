from object_search import *
from bind_functions import *
from global_variables import *
from storage_functions import *

from json import dumps, loads
from discord import DMChannel, Embed
from secret_variables import DEBUG_MODE
from card_search import get_creature_card
from global_variables import CUSTOM_EMOJIS
from dynamodb_methods import ddb_insert_item
from string_processing import burgl_message, capitalise_object_name


# returns True if message author is elevated, otherwise False
def check_user_elevation(message):
	return message.author.id in ELEVATED_USERS


# all bot methods below have to correspond to an item in BOT_COMMAND_LIST
# and must share the same name, followed by '_method'

# help menu method
async def help_method(bot, message, user_input, flag_presence):
	help_menu = Embed(description=f"{CUSTOM_EMOJIS['BURG.L']} **Command List**", colour=0x6542E1)

	for command in BOT_HELP_MENU:
		help_menu.add_field(name=command[0], value='\n'.join(command[1:]), inline=False)

	embedded_message = await message.channel.send(embed=help_menu)
	await embedded_message.add_reaction(CUSTOM_EMOJIS['CrossMark'])


	# returns True if emoji reaction by user to the specific help message is the cross mark
	def cross_emoji_check(reaction, user):
		return user != bot.user and reaction.message.id == embedded_message.id and reaction.emoji == CUSTOM_EMOJIS['CrossMark']


	while True:
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=60, check=cross_emoji_check)

			# check if channel is a private chat
			if isinstance(message.channel, DMChannel):
				return await embedded_message.delete()

			else:
				# close help menu
				await embedded_message.clear_reactions()
				return await embedded_message.edit(content=burgl_message('embed_close'), embed=None)

		except TimeoutError:
			try:
				# remove cross 'button' from the message
				return await embedded_message.clear_reactions()
			except:
				return


# object search method
async def search_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	result = None

	# if user forces search of actual query, then bypass both shortcut table as well as cache
	if not flag_presence['force_search']:

		# check if corresponding object info exists in cache
		result = retrieve_from_cache(OBJECT_INFO_CACHE, user_input)

		if result:
			# load dictionary from stored string
			result = loads(result)

			if isinstance(result, dict):
				# reinitialise collections.Counter for relevant attributes
				counter_list = ['recipe', 'repair_cost']

				for attribute in counter_list:
					if attribute in result:
						result[attribute] = Counter(result[attribute])

	# if query not in cache or -f flag present
	if not result:
		if flag_presence['force_search']:
			full_name = user_input
		else:
			full_name = retrieve_full_name(user_input)

		# extract object info
		result = get_object_info(full_name)

		# cache results except Google API error (the API could become available again at any time) and -f searches
		if result != 103 and not flag_presence['force_search'] and not DEBUG_MODE:
			ddb_insert_item(OBJECT_INFO_CACHE, user_input, dumps(result))

	if isinstance(result, list):
		# item page format is not supported
		if result[0] == 102:
			await message.channel.send(burgl_message(102).replace('VAR1', result[1]))

	# unable to locate item page URL
	elif result == 101:
		user_input = capitalise_object_name(user_input)
		await message.channel.send(burgl_message(101).replace('VAR1', user_input))

	# daily quota for Google API exhausted
	elif result == 103:
		await message.channel.send(burgl_message(103))

	else:
		await message.channel.send(embed=format_object_info(result))


# creature card search method
async def card_method(bot, message, user_input, flag_presence):
	if user_input == '':
		return await message.channel.send(burgl_message('empty'))

	# check for existing shortcut binding in database if no -f flag
	if not flag_presence['force_search']:
		full_name = retrieve_full_name(user_input)

	result = get_creature_card(full_name, flag_presence['get_gold'])

	# daily quota for Google API exhausted
	if result == 103:
		await message.channel.send(burgl_message(103))

	# card cannot be found
	elif result == 104:
		user_input = capitalise_object_name(user_input)
		await message.channel.send(burgl_message(104).replace('VAR1', user_input))

	else:
		embedded_card = Embed(title=f'{result[0]}', colour=0x6542E1)
		embedded_card.set_image(url=result[1])
		embedded_card.set_footer(text='Creature Card')

		await message.channel.send(embed=embedded_card)


# shortcut binding method
async def bind_method(bot, message, user_input, flag_presence):
	if flag_presence['view_bindings']:
		await bind_view(bot, message, user_input)

	# allow non-elevated users to view bindings
	if not check_user_elevation(message):
		return await message.channel.send(burgl_message('unauthorised'))

	if flag_presence['delete_binding']:
		if user_input == '':
			return await message.channel.send(burgl_message('empty'))

		await bind_delete(message, user_input)

	else:
		await bind_default(message, user_input)


# cache purging method
async def purge_method(bot, message, user_input, flag_presence):
	if not check_user_elevation(message):
		return await message.channel.send(burgl_message('unauthorised'))
	else:
		purge_cache()
		return await message.channel.send(burgl_message('purged'))


# message clearing method
async def clear_method(bot, message, user_input, flag_presence):
	message_history = [old_message async for old_message in message.channel.history()]

	# if message is from a server channel
	if not isinstance(message.channel, DMChannel):
		await message.channel.delete_messages(message_history)
		return await message.delete()

	else:  # if message is from a private message
		for old_message in message_history:
			if old_message.author == bot.user:
				await old_message.delete()
