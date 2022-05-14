from object_extraction import *
from string_processing import *

from discord import Embed
from url_processing import locate_object_url


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
def get_object_info(search_query, is_modifier):
	if is_modifier:  # check for status effect or modifier first
		modifier_info = get_modifier_info(search_query)

		if modifier_info:
			return modifier_info

	# check for special queries, e.g. upgraded tools, special smoothie types
	is_upgraded_tool = '+' == search_query.strip()[-1]
	search_query, smoothie_type = detect_smoothie_type(search_query)

	# get most likely wiki URL of object
	result = locate_object_url(search_query)

	if result is None:  # unable to locate URL for item
		return 101
	elif not result:  # Google API daily resource exhausted
		return 103

	page_content, page_title = result[0], result[1]

	try:
		object_info = get_infobox_info(page_content)
	except:
		# page layout not supported
		return [102, page_title]

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

	return object_info


# returns a discord.Embed message, displaying the extracted object information in a presentable format
def format_object_info(object_info):
	object_name = object_info['name']

	# append pet icon if the object is a tameable creature
	if 'tamewith' in object_info:
		object_name = pet_icon_emoji(object_name)

	# append elemental icon if the object is an elemental weapon
	elif 'augmenttype' in object_info:
		object_name = elemental_weapon_emoji(object_name, object_info['augmenttype'])

	embedded_info = Embed(title=object_name, colour=0x6542E1)
	embedded_info.set_image(url=object_info['picture_url'])


	# subfunction to add field to embed message
	# if no special_name given, then the displayed name will just be capitalised attribute name
	# if special_value is provided, it will override the dictionary value
	def insert_embed_field(attribute, inline, special_name=None, special_value=None):

		# check if attribute exists for that object
		if attribute in object_info:

			if special_name:
				attribute_name = special_name
			else:
				attribute_name = attribute.title()

			if special_value:
				value = special_value
			else:
				value = object_info[attribute]

			embedded_info.add_field(name=attribute_name, value=value, inline=inline)


	if 'description' in object_info:
		embedded_info.add_field(name='Description', value=f"*{object_info['description']}*", inline=False)

	# modifiers
	insert_embed_field('source', False, special_name='Source(s)')

	# common flow
	for attribute in ['category', 'aggression', 'tier']:
		insert_embed_field(attribute, False)

	# resource nodes
	insert_embed_field('brokenwith', False, special_name='Harvest with')

	# creatures
	insert_embed_field('tamewith', False, special_name='Tame with')
	insert_embed_field('effectresistance', False, special_name='Effect Resistance')

	if 'resistance' in object_info:
		embedded_info.add_field(name='Dmg. Resistance', value=damage_elemental_emoji(object_info['resistance']), inline=False)
	if 'eresistance' in object_info:
		embedded_info.add_field(name='Elem. Resistance', value=damage_elemental_emoji(object_info['eresistance']), inline=False)
	if 'weakness' in object_info:
		embedded_info.add_field(name='Dmg. Weakness', value=f"__{damage_elemental_emoji(object_info['weakness'])}__".replace(', ', '__, __'), inline=False)
	if 'eweakness' in object_info:
		embedded_info.add_field(name='Elem. Weakness', value=f"__{damage_elemental_emoji(object_info['eweakness'])}__".replace(', ', '__, __'), inline=False)
	if 'weakpoint' in object_info:
		embedded_info.add_field(name='Weak Point', value=f"__{object_info['weakpoint']}__", inline=False)

	# items
	if 'tooltype' in object_info:
		embedded_info.add_field(name='Dmg. Type', value=damage_elemental_emoji(object_info['tooltype']), inline=False)

	insert_embed_field('class', False, special_name='Armor Class')

	if 'food' in object_info:
		# account for special cases of food with Fresh versions
		embedded_info.add_field(name='Food', value=object_info['food'].replace(')+', '); +'), inline=False)

	# common flow
	for attribute in ['loot', 'damage', 'stun', 'speed', 'defense', 'water', 'health', 'sturdiness', 'weight', 'species', 'gender']:
		insert_embed_field(attribute, False)

	if 'effects' in object_info:
		embedded_info.add_field(name='Effects', value=', '.join(object_info['effects']), inline=False)

	insert_embed_field('upgradeeffect', False, special_name='Sleek Upgrade Effect')

	if 'recipe' in object_info:
		recipe_name = 'Recipe'

		# check if recipe crafts multiple items
		if object_info['recipe_name']:
			recipe_name += f": {object_info['recipe_name']}"

		recipe_list = generate_recipe_string(object_info['recipe'])
		embedded_info.add_field(name=recipe_name, value=recipe_list, inline=False)

	if 'repair_cost' in object_info:
		repair_list = generate_recipe_string(object_info['repair_cost'])
		embedded_info.add_field(name='Repair Cost', value=repair_list, inline=False)

	return embedded_info
