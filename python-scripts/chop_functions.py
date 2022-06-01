from math import ceil
from discord import Embed

from bot_messaging import *
from chop_processing import *
from global_variables import *
from storage_functions import *
from string_processing import *


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

		# skip item if given quantity is 0
		if initial_quantity == 0:
			continue

		item_entry = process_chop_components(item_name, initial_quantity)

		if not await detect_search_errors(message, item_name, item_entry):
			continue

		actual_name, final_quantity, base_components = item_entry

		# generate component string here instead of after database insertion as base_components gets updated with existing quantities
		base_components_string = generate_recipe_string(base_components)

		if insert_chop_item(actual_name, final_quantity, base_components):

			# TODO: Forward base_components Counter to Task Scheduler

			summary_embed.add_field(name=f'{CUSTOM_EMOJIS[index]} {actual_name} (x{final_quantity})', value=base_components_string, inline=False)
			index += 1

	# exit if no valid items were added
	if len(summary_embed) == len(embed_title):
		return

	# TODO: Create Embed handler to insert 9 emojis and wait for responses

	await message.channel.send(embed=summary_embed)


# view current Chopping List entries
async def chop_view(bot, message, user_input):
	chopping_list = retrieve_chopping_list()

	embed_list = []
	number_pages = ceil(len(chopping_list) / MAX_CHOPPING_FIELDS)

	for page in range(number_pages):
		chopping_embed = Embed(title='**Chopping List**', color=EMBED_COLOR_CODE)

		start_index = page * MAX_CHOPPING_FIELDS
		end_index = start_index + MAX_CHOPPING_FIELDS

		for entry in chopping_list[start_index:end_index]:
			item = entry[0]
			quantity = entry[1][0]
			components = generate_recipe_string(entry[1][1])

			chopping_embed.add_field(name=f'{item} (x{quantity})', value=components, inline=False)

		chopping_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(chopping_embed)

	return await multipage_embed_handler(bot, message, user_input, embed_list)


# complete/delete items on the Chopping List
async def chop_delete(message, user_input):
	input_items = process_chop_input(user_input, True)

	if not input_items:
		return await burgl_message('empty', message)

	# retrieve current Chopping List and convert to dictionary
	chopping_list = dict(retrieve_chopping_list())

	string_header = 'Items checked off the Chopping List:\n'
	formatted_string = ''

	# process each item name input and check if it exists in the Chopping List
	for input_name, input_quantity in input_items.items():

		# parse input through search algorithm
		item_info = process_object_input(input_name)

		# additional error detection
		if isinstance(item_info, dict):

			# prefix smoothie type to smoothie name
			if 'category' in item_info and 'smoothie' in item_info['category'].lower():
				item_name = item_info['recipe_name']
			else:
				item_name = item_info['name']

			if not check_valid_item(item_info):
				item_info = 105
			elif item_name not in chopping_list:
				item_info = 106

			# update input name for error handling
			input_name = item_name

		if not await detect_search_errors(message, input_name, item_info):
			continue

		existing_quantity = chopping_list[item_name][0]
		base_components = chopping_list[item_name][1]

		# if existing quantity is smaller than or equal to input quantity, then remove entire entry
		if existing_quantity <= input_quantity:
			input_quantity = -1

		# delete entire entry if quantity is -1
		if input_quantity == -1:
			ddb_remove_item(CHOPPING_LIST, item_name)
			input_quantity = 'All'

		# otherwise, deduct item quantity and adjust component quantities correspondingly
		else:
			new_quantity = existing_quantity - input_quantity
			ratio = new_quantity / existing_quantity
			input_quantity = f'x{input_quantity}'

			for material in base_components:
				base_components[material] = int(base_components[material] * ratio)

			# update Chopping List entry
			insert_chop_item(item_name, new_quantity, base_components, True)

		formatted_string += f'- **{item_name} ({input_quantity})**\n'

	# send string to acknowledge entry deletion
	if formatted_string:
		await message.channel.send(string_header + formatted_string)
