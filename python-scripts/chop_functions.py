from bot_messaging import *
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

	summary_embed = Embed(title='**Chopping List - New Items**', color=EMBED_COLOR_CODE)
	empty_summary = summary_embed.copy()

	for item_name, initial_quantity in chopping_items.items():
		item_entry = process_chop_components(item_name, initial_quantity)

		if await detect_search_errors(message, item_name, item_entry):
			actual_name, final_quantity, base_components = item_entry
			base_components_string = generate_recipe_string(base_components)

			if actual_name in base_components_string:
				base_components_string = '\u200b'

			summary_embed.add_field(name=f'{actual_name} (x{final_quantity})', value=base_components_string, inline=False)

	if len(summary_embed) != len(empty_summary):
		await message.channel.send(embed=summary_embed)
