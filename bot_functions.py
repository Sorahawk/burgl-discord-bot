import string

from object_search import *
from supplementary_extraction import get_creature_card


# object search method
async def search_function(message, search_query):
	if search_query == '':
		await message.channel.send('Please provide an input query.')
		return

	result = get_object_info(search_query)

	if isinstance(result, tuple):
		# item page format is not supported
		if result[0] == 102:
			await message.channel.send(f"**ERROR 102:** Wiki page for '{result[1]}' has an unsupported layout.")

	# unable to locate item page URL
	elif result == 101:
		await message.channel.send(f"**ERROR 101:** Unable to locate '{string.capwords(search_query)}'. Try typing in the object's full name.")

	# daily quota for Google API exhausted
	elif result == 103:
		await message.channel.send(f'**ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.')

	else:
		await message.channel.send(result['picture_url'])
		await message.channel.send(format_object_info(result))


# creature card search method
async def card_function(message, search_query):
	if search_query == '':
		await message.channel.send('Please provide an input query.')
		return

	creature_card = get_creature_card(search_query)

	# card cannot be found
	if creature_card == 104:
		if '.' in search_query:
			search_query = search_query.upper()
		else:
			search_query = search_query.title()

		await message.channel.send(f"**ERROR 104:** Unable to locate Creature Card for '{search_query}'. Type in the exact name of the creature.")

	else:
		await message.channel.send(creature_card)
