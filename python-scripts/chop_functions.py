from chop_processing import *
from global_variables import *


# default subfunction to add at least one item to the Chopping List
async def chop_default(message, user_input):
	# process user input into dictionary of items and their desired quantities
	chopping_items = process_chop_input(user_input)

	if not chopping_items:
		return await burgl_message('empty', message)

	elif len(chopping_items) > MAX_CHOPPING_INPUT:
		return await burgl_message('exceeded', message)

	for item, quantity in chopping_items.items():
		print(process_chop_components(item, quantity))







	'''summary_embed = Embed(title='**Chopping List - New Items**', color=EMBED_COLOR_CODE)
	empty_summary = summary_embed.copy()

	for item_name, quantity in chopping_items.items():
		added_items = process_chop_components(item_name, quantity)

		# check for errors and proceed if none detected
		if await detect_search_errors(message, item_name, added_items):
			item_name = added_items['name']
			item_quantity = added_items['quantity']

			del added_items['name']
			del added_items['quantity']

			added_items = generate_recipe_string(added_items)
			summary_embed.add_field(name=f'{item_name} (x{item_quantity})', value=added_items, inline=False)

	# print summary of added materials
	if len(summary_embed) != len(empty_summary):
		await message.channel.send(embed=summary_embed)'''
