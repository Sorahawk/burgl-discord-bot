from var_global import *
from bot_messaging import *
from storage_functions import *
from string_processing import *

from math import ceil
from discord import Embed
from re import findall, IGNORECASE


# bind one or more shortcuts to a full object name
async def bind_default(message, user_input):
	name_pattern = "[a-z ._+'?-]+"
	results = findall(name_pattern, user_input, IGNORECASE)

	if len(results) < 2:
		return await burgl_message('insufficient', message)

	formatted_string = bind_shortcuts(results[0], results[1:])
	await message.channel.send(formatted_string)


# view all existing bindings
async def bind_view(message, user_input):
	shortcut_list = retrieve_all_shortcuts()

	# create embeds until all shortcuts are in a page
	embed_list = []
	number_pages = ceil(len(shortcut_list) / MAX_SHORTCUT_FIELDS)

	for page in range(number_pages):
		shortcut_embed = Embed(title='**Binded Shortcuts**', color=EMBED_COLOR_CODE)

		start_index = page * MAX_SHORTCUT_FIELDS
		end_index = start_index + MAX_SHORTCUT_FIELDS

		for binded_pair in shortcut_list[start_index:end_index]:
			shortcuts = ', '.join(binded_pair[1])
			shortcut_embed.add_field(name=binded_pair[0], value=f'*{shortcuts}*', inline=False)

		shortcut_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(shortcut_embed)

	return await multipage_embed_handler(message, user_input, embed_list)


# delete all shortcuts for one or more specified object names
async def bind_delete(message, user_input):
	string_header = 'All shortcuts removed for the following:\n'
	formatted_string = ''

	all_shortcuts = dict(retrieve_all_shortcuts())

	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	for item_name in user_input:
		result = delete_shortcut(item_name, all_shortcuts)

		# if shortcut not found, move to next one inputted
		if not await detect_errors(message, item_name, result):
			continue

		formatted_string += f'- **{custom_capitalise_string(item_name)}**\n'

	if formatted_string:
		await message.channel.send(string_header + formatted_string)
