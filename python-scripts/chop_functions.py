from math import ceil
from discord import Embed

from bot_messaging import *
from chop_processing import *
from global_constants import *
from storage_functions import *
from string_processing import *


# add one or more items to the Chopping List
async def chop_default(message, user_input):
	# process user input into dictionary of items and their desired quantities
	chopping_items = process_chop_input(user_input)

	if not chopping_items:
		return await burgl_message('empty', message)

	elif len(chopping_items) > MAX_CHOPPING_INPUT:
		return await burgl_message('chop_exceeded', message)

	# acknowledge user command because waiting time might be a bit long
	reply = await burgl_message('processing', message)

	embed_title = '**Chopping List - New Items**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	for item_name, initial_quantity in chopping_items.items():
		item_entry = process_chop_components(item_name, initial_quantity)

		if not await detect_errors(message, item_name, item_entry):
			continue

		# proceed with item insertion
		summary_embed = insert_chop_item(item_entry, summary_embed)

	# only send embed if valid items were added
	if len(summary_embed) != len(embed_title):
		await message.channel.send(embed=summary_embed)

	# delete earlier acknowledgement message
	await reply.delete()


# view current Chopping List entries
async def chop_view(message, user_input):
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

	return await multipage_embed_handler(message, user_input, embed_list)


# check one or more items off the Chopping List
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

			if not check_valid_chop_item(item_info):
				item_info = 105
			elif item_name not in chopping_list:
				item_info = 106

			# update input name for error handling
			input_name = item_name

		if not await detect_errors(message, input_name, item_info):
			continue

		# proceed with item deletion
		input_quantity = remove_chop_item(item_name, item_info, input_quantity, chopping_list)
		formatted_string += f'- **{item_name} (x{input_quantity})**\n'

	# send string to acknowledge entry deletion
	if formatted_string:
		await message.channel.send(string_header + formatted_string)


# wipe the entire Chopping List
async def chop_reset(message, user_input):
	if 'confirm' not in user_input.lower():
		return await burgl_message('need_confirmation', message)

	chopping_list = retrieve_chopping_list()

	for item in chopping_list:
		item_name = item[0]

		ddb_remove_item(CHOPPING_TABLE, item_name)


	# TODO: Remove all generated harvesting tasks from Task Scheduler


	await burgl_message('chop_reset', message)
