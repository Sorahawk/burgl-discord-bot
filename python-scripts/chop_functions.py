from math import ceil
from discord import Embed

from bot_messaging import *
from chop_processing import *
from global_variables import *
from storage_functions import *


# default subfunction to add at least one item to the Chopping List
async def chop_default(message, user_input):
	# process user input into dictionary of items and their desired quantities
	chopping_items = process_chop_input(user_input)

	if not chopping_items:
		return await burgl_message('empty', message)

	elif len(chopping_items) > MAX_CHOPPING_INPUT:
		return await burgl_message('chop_exceeded', message)

	embed_title = '**Chopping List - New Items**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	index = 1
	for item_name, initial_quantity in chopping_items.items():
		item_entry = process_chop_components(item_name, initial_quantity)

		if await detect_search_errors(message, item_name, item_entry):
			actual_name, final_quantity, base_components = item_entry

			# update item quantities in Chopping List
			if insert_chop_item(actual_name, final_quantity, base_components):

				# TODO: Forward base_components Counter to Task Scheduler

				base_components_string = generate_recipe_string(base_components)

				summary_embed.add_field(name=f'{CUSTOM_EMOJIS[index]} {actual_name} (x{final_quantity})', value=base_components_string, inline=False)
				index += 1

	if len(summary_embed) == len(embed_title):  # if no valid items were added
		await burgl_message('empty', message)
	else:

		# TODO: Create Embed handler to insert 9 emojis and wait for delete

		await message.channel.send(embed=summary_embed)


# view current Chopping List entries
async def chop_view(bot, message, user_input):
	chopping_list = ddb_retrieve_all(CHOPPING_LIST)

	embed_list = []
	number_pages = ceil(len(chopping_list) / MAX_CHOPPING_FIELDS)

	for page in range(number_pages):
		chopping_embed = Embed(title='**Chopping List**', color=EMBED_COLOR_CODE)

		start_index = page * MAX_CHOPPING_FIELDS
		end_index = start_index + MAX_CHOPPING_FIELDS

		for entry in chopping_list[start_index:end_index]:
			item = entry['item']
			quantity = entry['quantity']
			components = generate_recipe_string(entry['components'])

			chopping_embed.add_field(name=f'{item} (x{quantity})', value=components, inline=False)

		chopping_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(chopping_embed)

	return await multipage_embed_handler(bot, message, user_input, embed_list)
