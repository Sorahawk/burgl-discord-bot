import math

from discord import Embed

from bot_messaging import *
from global_variables import *
from storage_functions import *
from string_processing import *


# default subfunction to bind at least one shortcut to a full object name
async def bind_default(message, user_input):
	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	if len(user_input) < 2:
		return await burgl_message('insufficient', message)

	formatted_string = bind_shortcuts(user_input[0], user_input[1:])
	await message.channel.send(formatted_string)


# view all existing bindings
async def bind_view(bot, message, user_input):
	shortcut_list = retrieve_all_shortcuts()

	# create embeds until all shortcuts are in a page (max fields per page can be manually set, but the actual max by Discord is 25)
	embed_list = []
	number_pages = math.ceil(len(shortcut_list) / MAX_SHORTCUT_FIELDS)

	for page in range(number_pages):
		shortcut_embed = Embed(title='**Binded Shortcuts**', color=EMBED_COLOR_CODE)

		start_index = page * MAX_SHORTCUT_FIELDS
		end_index = start_index + MAX_SHORTCUT_FIELDS

		for binded_pair in shortcut_list[start_index:end_index]:
			shortcuts = ', '.join(binded_pair[1])
			shortcut_embed.add_field(name=binded_pair[0], value=f'*{shortcuts}*', inline=False)

		shortcut_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(shortcut_embed)

	return await multipage_embed_handler(bot, message, user_input, embed_list)


# delete all shortcuts for one or more specified object names
async def bind_delete(message, user_input):
	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	formatted_string = delete_shortcuts(user_input)

	if formatted_string:
		await message.channel.send(formatted_string)
	else:
		await burgl_message('invalid_bind', message)
