import string

from object_search import get_object_info, format_object_info


# object search function
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
