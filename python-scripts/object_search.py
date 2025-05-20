import var_global

from var_global import *
from url_processing import *
from object_extraction import *
from string_processing import *

from discord import Embed
from json import dumps, loads
from collections import Counter


# returns tuple of booleans representing presence of recipe and repair costs on an object's page
def check_info_presence(page_content):
	has_recipe = True
	has_repair_cost = False

	# check for presence of element ID 'Recipe'
	try:
		page_content.get_element_by_id('Recipe')
	except:
		has_recipe = False

	# if 'Recipe' not found, search again for 'Recipes'
	if not has_recipe:
		try:
			page_content.get_element_by_id('Recipes')
			has_recipe = True
		except:
			pass

	for text in page_content.itertext():
		if 'Repair Cost' in text.strip():
			has_repair_cost = True

	return has_recipe, has_repair_cost


# returns True if page is for an armor set, otherwise returns None by default
def check_armor_set_page(page_content):
	try:
		page_content.get_element_by_id('Armor_Set')
		return True
	except:
		pass


# used when normal object search fails to check if search query is referring to special objects
def get_special_info(search_query, page_title=None):

	# check if it is a piece within an armor set
	if page_title and page_title != 'Armor':
		# if object search already redirected to a specific armor set page, then no need to match input to armor set
		queried_set = page_title.replace('Armor', '').strip()
	else:
		queried_set = match_armor_set(search_query)

	if queried_set:
		item_info = get_armor_piece_info(search_query, queried_set)

		if item_info:
			return item_info

	# check if it is a modifier
	return get_modifier_info(search_query)


# returns dictionary of extracted information for an input object, or error codes if an error occurs
def get_object_info(search_query):

	# run search query through special routes first
	info_result = get_special_info(search_query)

	if info_result:
		return info_result

	# check for special queries, e.g. upgraded tools
	is_upgraded_tool = '+' in search_query

	# get most likely wiki URL of object
	result = locate_object_url(search_query)

	if result is None:
		# unable to locate URL for item
		return 101

	# Google API daily resource exhausted
	elif result is False:
		return 103

	page_content, page_title = result[0], result[1]

	# reject pages on the blacklist as unsupported
	if page_title in WIKI_PAGE_BLACKLIST:
		return [102, page_title]

	try:
		object_info = get_infobox_info(page_content)
		object_info['page_url'] = result[2]

	except:
		# page layout not supported
		return [102, page_title]

	# if query searching for upgraded tool, check for presence of both description+ and tier+
	if is_upgraded_tool and ('description+' in object_info or 'tier+' in object_info):
		object_info['name'] += '+'

		if 'description+' in object_info:
			object_info['description'] = object_info['description+']
		if 'tier+' in object_info:
			object_info['tier'] = object_info['tier+']

		# Fin Flops+ has different upgraded effect, so have to replace the original
		if 'effect+' in object_info:
			object_info['effects'] = object_info['effect+']

	has_recipe, has_repair_cost = check_info_presence(page_content)

	# disable recipe extraction for natural resources since some items like Plant Fiber can be grinded
	if 'category' in object_info and object_info['category'] == 'Natural Resources':
		has_recipe, has_repair_cost = False, False

	if has_recipe:
		try:
			full_recipe_list = get_recipe_tables(page_content, object_info['name'])

			# check for multiple recipes
			if len(full_recipe_list) > 1:

				# Fiber Bandage special case - use upgraded recipe
				if object_info['name'] == 'Fiber Bandage':
					object_info['recipe_name'], object_info['recipe'] = full_recipe_list[1]

				else:
					object_info['recipe_name'] = ''
					object_info['recipe'] = 'Multiple Recipes'

			else:
				object_info['recipe_name'], object_info['recipe'] = full_recipe_list[0]

		except:
			# recipe extraction failed
			var_global.OPERATIONS_LOG.warning(f"Recipe extraction for {object_info['name']} failed.")

	if has_repair_cost:
		try:
			object_info['repair_cost'] = get_repair_cost(page_content)
		except:
			# repair cost extraction failed
			var_global.OPERATIONS_LOG.warning(f"Repair cost extraction for {object_info['name']} failed.")

	return object_info


# returns a dictionary containing attributes of the searched object if located
# otherwise, can return error codes 101, 102 or 103 depending on the failure case
# function also caches results for succesful retrieval, as well as errors 101 and 102
def process_object_input(user_input, flag_presence={'override': False}):

	# detect smoothie type
	# processing this at the start means that smoothie types can be processed independently from shortened smoothie names
	# however, as a result the smoothie type keywords (e.g. beefy, sticky) cannot be used as part of shortnames (e.g. sticky bomb) as they will be removed
	user_input, smoothie_type = detect_smoothie_type(user_input)

	result = None

	# if no override, check if cache contains requested data
	if not flag_presence['override']:

		# check if corresponding object info exists in cache
		result = retrieve_from_cache(INFO_TABLE, user_input)

		if result:
			# load dictionary from stored string
			result = loads(result)

			if isinstance(result, dict):
				# reinitialise collections.Counter for relevant attributes
				counter_list = ['recipe', 'repair_cost']

				for attribute in counter_list:
					if attribute in result:

						# account for case where object has multiple recipes
						if isinstance(result[attribute], str):
							continue

						result[attribute] = Counter(result[attribute])

	# if data not found in cache
	if not result:
		# retrieve full name from shortcut table if no override
		if flag_presence['override']:
			full_name = user_input
		else:
			full_name = retrieve_full_name(user_input)

		# extract object info
		result = get_object_info(full_name)

		# cache results except when override flag is present, or Google API error occurs (API could be available again at any time)
		if result != 103 and not flag_presence['override'] and not DEBUG_MODE:
			ddb_insert_item(INFO_TABLE, user_input, dumps(result))

	# most attributes of smoothies are cached, except their smoothie base ingredient, since it is variable
	if isinstance(result, dict) and 'category' in result and 'smoothie' in result['category'].lower():
		result = insert_smoothie_base(result, smoothie_type)

	return result


# returns a grid-formatted embed message with blank fields to be filled in with attributes
def create_grid_embed(title, url, image):
	embedded_message = Embed(title=title, url=url, color=EMBED_COLOR_CODE)
	embedded_message.set_image(url=image)

	embedded_message.add_field(name='Description', value='\u200b', inline=False)

	for field_num in range(15):
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
		embedded_info.set_field_at(1, name='Harvest with', value=prefix_custom_emoji(object_info['brokenwith']), inline=True)

	if 'tooltype' in object_info:
		embedded_info.set_field_at(3, name='Dmg. Type', value=prefix_custom_emoji(object_info['tooltype']), inline=True)
	if 'class' in object_info:
		embedded_info.set_field_at(3, name='Armor Class', value=prefix_custom_emoji(object_info['class']), inline=True)

	if 'eresistance' in object_info:
		embedded_info.set_field_at(7, name='Elem. Resistance', value=prefix_custom_emoji(object_info['eresistance']), inline=True)
	if 'resistance' in object_info:
		resist_name = 'Resistance'

		# check if search object is a creature
		if 'aggression' in object_info:
			resist_name = f"Dmg. {resist_name}"

		embedded_info.set_field_at(8, name=resist_name, value=prefix_custom_emoji(object_info['resistance']), inline=True)

	if 'eweakness' in object_info:
		embedded_info.set_field_at(10, name='Elem. Weakness', value=underline_text(prefix_custom_emoji(object_info['eweakness'])), inline=True)
	if 'weakness' in object_info:
		embedded_info.set_field_at(11, name='Dmg. Weakness', value=underline_text(prefix_custom_emoji(object_info['weakness'])), inline=True)

	if 'weakpoint' in object_info:
		is_robot = False
		if '.' in object_name:
			is_robot = True

		embedded_info.set_field_at(12, name='Weak Point', value=underline_text(prefix_custom_emoji(object_info['weakpoint'], is_robot)), inline=True)

	if 'recipe' in object_info:
		recipe_name = 'Recipe'

		# account for objects with multiple recipes
		if isinstance(object_info['recipe'], str):
			recipe_list = object_info['recipe']

		else:
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

	# look for and process specific cases of empty embed fields
	# start from bottom up so deleting fields won't affect the index while checking the fields on top

	# check each row (indexes 1-3, 4-6, 7-9, 10-12)
	for row_index in range(15, 0, -3):
		field_indices = [row_index - 2, row_index - 1, row_index]  # left, middle, right

		# generate a corresponding list of booleans that represent whether each field is empty
		fields_empty = [embedded_info.fields[field_index].value == '\u200b' for field_index in field_indices]

		# calculate the number of True values in the list
		num_empty = sum(fields_empty)

		# all True; entire row is empty
		if num_empty == 3:
			# delete entire row from right to left
			for field_index in field_indices[::-1]:
				embedded_info.remove_field(field_index)

		# only one field has content
		elif num_empty == 2:
			# traverse the row from right to left, deleting the empty fields and editing the remaining one to take up the entire row
			for count in range(2, -1, -1):
				field_index = field_indices[count]
				is_empty = fields_empty[count]

				if is_empty:
					embedded_info.remove_field(field_index)
				else:
					# edit the field to take up the entire row by switching inline to False
					field = embedded_info.fields[field_index]
					embedded_info.set_field_at(field_index, name=field.name, value=field.value, inline=False)

	# check if description is empty
	if embedded_info.fields[0].value == '\u200b':
		embedded_info.remove_field(0)

	return embedded_info
