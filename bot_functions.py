import json, string

from object_search import *
from global_variables import *
from storage_functions import *
from card_search import get_creature_card
from dynamodb_methods import ddb_insert_item
from helper_functions import check_command_flag


# object search method
async def search_method(message, search_query):

	# check for modifier (status effects & mutations) flag
	is_modifier, search_query = check_command_flag(search_query, 'modifier')

	# check if corresponding object info exists in cache
	result = retrieve_from_cache(OBJECT_INFO_CACHE, search_query)

	if result:
		# load dictionary from stored string
		result = json.loads(result)

		if isinstance(result, dict):
			# reinitialise collections.Counter for relevant attributes
			counter_list = ['recipe', 'repair_cost']

			for attribute in counter_list:
				if attribute in result:
					result[attribute] = Counter(result[attribute])

		elif is_modifier:
			# if user searches for a modifier without the -m flag, it will cache 101 or 102 error, which will make any subsequent queries with the -m flag to fail as well
			# thus if cache contains error, but query has -m flag, override cache and extract modifier info
			result = None

	# create a new 'if' rather than using 'else' because of the is_modifier case right above
	if not result:
		# check for existing shortcut binding in database
		full_name = retrieve_full_name(search_query)

		# extract object info
		result = get_object_info(full_name, is_modifier)

		# cache results except Google API error (the API could become available again at any time)
		if result != 103:
			ddb_insert_item(OBJECT_INFO_CACHE, search_query, json.dumps(result))

	if isinstance(result, list):
		# item page format is not supported
		if result[0] == 102:
			await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 102:** Wiki page for '{result[1]}' has an unsupported layout.")

	# unable to locate item page URL
	elif result == 101:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 101:** Unable to locate '{string.capwords(search_query)}'. Try typing in the object's full name.")

	# daily quota for Google API exhausted
	elif result == 103:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.")

	else:
		await message.channel.send(result['picture_url'])
		await message.channel.send(format_object_info(result))


# creature card search method
async def card_method(message, search_query):
	search_query = retrieve_full_name(search_query)  # check for existing shortcut binding in database
	result = get_creature_card(search_query)

	if result == 103:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.")

	# card cannot be found
	elif result == 104:
		if '.' in search_query:
			search_query = search_query.upper()
		else:
			search_query = search_query.title()

		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} **ERROR 104:** Unable to locate Creature Card for '{search_query}'. Type in the exact name of the creature.")

	else:
		await message.channel.send(f'**Creature Name:** {result[0]}')
		await message.channel.send(result[1])


# linking shortcut query method
async def bind_method(message, user_input):

	# remove any edge commas before splitting by comma
	user_input = user_input.lower().strip(',').split(',')

	if len(user_input) < 2:
		await message.channel.send(f"{CUSTOM_EMOJIS['BURG.L']} A minimum of two parameters are required.")
		return

	formatted_string = bind_query_name(user_input[0], user_input[1:])
	await message.channel.send(formatted_string)
