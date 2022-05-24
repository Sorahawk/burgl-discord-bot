from discord import Embed

from url_processing import *
from global_variables import *
from object_extraction import *
from string_processing import *


# returns booleans representing presence of recipe and repair costs on an object's page
def check_info_presence(page_content):
	has_recipe = True
	has_repair_cost = False

	try:
		page_content.get_element_by_id('Recipe')
	except KeyError:
		has_recipe = False

	if 'Repair Cost' in page_content.itertext():
		has_repair_cost = True

	return has_recipe, has_repair_cost


# returns dictionary of extracted information for an input object, or error codes if an error occurs
def get_object_info(search_query):

	# check for special queries, e.g. upgraded tools, special smoothie types
	is_upgraded_tool = '+' in search_query
	search_query, smoothie_type = detect_smoothie_type(search_query)

	# get most likely wiki URL of object
	result = locate_object_url(search_query)

	# unable to locate URL for item
	if result is None:

		# check if it is a modifier
		modifier_info = get_modifier_info(search_query)
		return modifier_info if modifier_info else 101

	# Google API daily resource exhausted
	elif result is False:
		return 103

	page_content, page_title = result[0], result[1]

	try:
		object_info = get_infobox_info(page_content)
		object_info['page_url'] = result[2]

	except:  # page layout not supported

		# check if it is a modifier
		modifier_info = get_modifier_info(search_query)
		return modifier_info if modifier_info else [102, page_title]

	# if query searching for upgraded tool, check for presence of both description+ and tier+
	if is_upgraded_tool and 'description+' in object_info and 'tier+' in object_info:
		object_info['description'] = object_info['description+']
		object_info['tier'] = object_info['tier+']

	has_recipe, has_repair_cost = check_info_presence(page_content)

	if has_recipe:
		try:
			object_info['recipe'], object_info['recipe_name'] = get_recipe_table(page_content, object_info['name'], smoothie_type)
		except:
			# recipe extraction failed
			print(f"WARNING: Recipe extraction for {object_info['name']} failed.")

	if has_repair_cost:
		try:
			object_info['repair_cost'] = get_repair_cost(page_content)
		except:
			# repair cost extraction failed
			print(f"WARNING: Repair cost extraction for {object_info['name']} failed.")

	# if object is Smoothie?, manually insert recipe with just the base ingredient
	if object_info['name'] == 'Smoothie?':
		object_info['recipe_name'] = f'{smoothie_type.title()} Smoothie?'
		object_info['recipe'] = compile_counter([SMOOTHIE_BASES[smoothie_type]], 'Smoothie')

	return object_info


# returns a grid-formatted embed message with blank fields to be filled in with attributes
def create_grid_embed(title, url, image):
	embedded_message = Embed(title=title, url=url, color=EMBED_COLOR_CODE)
	embedded_message.set_image(url=image)

	embedded_message.add_field(name='Description', value='\u200b', inline=False)

	for field_num in range(12):
		embedded_message.add_field(name='\u200b', value='\u200b', inline=True)

	return embedded_message


# returns a discord.Embed message, displaying the extracted object information in a presentable format
def format_object_info(object_info):
	object_name = object_info['name']

	# append pet icon if the object is a tameable creature
	if 'tamewith' in object_info:
		object_name = append_pet_emoji(object_name)

	# append elemental icon if the object is an elemental weapon
	elif 'augmenttype' in object_info:
		object_name = append_elem_emoji(object_name, object_info['augmenttype'])

	# create empty grid embed
	embedded_info = create_grid_embed(object_name, object_info['page_url'], object_info['picture_url'])

	# fill in embed fields with attributes that are present in object_info
	if 'description' in object_info:
		embedded_info.set_field_at(0, name='Description', value=f"*{object_info['description']}*", inline=False)

	if 'brokenwith' in object_info:
		embedded_info.set_field_at(1, name='Harvest with', value=prefix_emoji(object_info['brokenwith']), inline=True)

	if 'tooltype' in object_info:
		embedded_info.set_field_at(3, name='Dmg. Type', value=prefix_emoji(object_info['tooltype']), inline=True)

	if 'class' in object_info:
		embedded_info.set_field_at(4, name='Armor Class', value=prefix_emoji(object_info['class']), inline=True)

	if 'resistance' in object_info:
		embedded_info.set_field_at(4, name='Dmg. Resistance', value=prefix_emoji(object_info['resistance']), inline=True)
	if 'eresistance' in object_info:
		embedded_info.set_field_at(5, name='Elem. Resistance', value=prefix_emoji(object_info['eresistance']), inline=True)

	if 'weakness' in object_info:
		embedded_info.set_field_at(7, name='Dmg. Weakness', value=underline_text(prefix_emoji(object_info['weakness'])), inline=True)
	if 'eweakness' in object_info:
		embedded_info.set_field_at(8, name='Elem. Weakness', value=underline_text(prefix_emoji(object_info['eweakness'])), inline=True)

	if 'weakpoint' in object_info:
		is_robot = False
		if '.' in object_name:
			is_robot = True

		embedded_info.set_field_at(9, name='Weak Point', value=underline_text(prefix_emoji(object_info['weakpoint'], is_robot)), inline=True)

	if 'recipe' in object_info:
		recipe_name = 'Recipe'

		# check if recipe crafts multiple items
		if object_info['recipe_name']:
			recipe_name += f": {object_info['recipe_name']}"

		recipe_list = generate_recipe_string(object_info['recipe'])
		embedded_info.set_field_at(10, name=recipe_name, value=recipe_list, inline=True)

	if 'repair_cost' in object_info:
		repair_list = generate_recipe_string(object_info['repair_cost'])
		embedded_info.set_field_at(11, name='Repair Cost', value=repair_list, inline=True)

	for attribute, attribute_info in OBJECT_ATTRIBUTES.items():
		if attribute in object_info:

			if isinstance(attribute_info, int):  # if no special name
				index = attribute_info
				attribute_name = attribute.title()

			else:
				index = attribute_info[0]
				attribute_name = attribute_info[1]

			embedded_info.set_field_at(index, name=attribute_name, value=object_info[attribute], inline=True)

	# look for any specific empty embed cases and process
	# start from bottom up so deleting fields won't affect the index while checking the fields on top

	# check each row (indexes 1-3, 4-6, 7-9, 10-12)
	for row_index in range(12, 3, -3):
		right_field = embedded_info.fields[row_index]
		middle_field = embedded_info.fields[row_index - 1]
		left_field = embedded_info.fields[row_index - 2]

		# check for empty rows
		if left_field.value  == '\u200b' and middle_field.value == '\u200b' and right_field.value == '\u200b':
			for count in range(3):
				embedded_info.remove_field(row_index - count)

	# if last row only has leftmost field, then let it take the whole row
	if embedded_info.fields[-1].value == '\u200b' and embedded_info.fields[-2].value == '\u200b':
		for count in range(2):
			embedded_info.remove_field(-1)

		field_name = embedded_info.fields[-1].name
		field_value = embedded_info.fields[-1].value
		embedded_info.set_field_at(-1, name=field_name, value=field_value, inline=False)

	# check if description is empty
	if embedded_info.fields[0].value == '\u200b':
		embedded_info.remove_field(0)

	return embedded_info
