from object_extraction import *
from supplementary_extraction import get_modifier_info
from url_processing import get_page_data, locate_object_url
from helper_functions import detect_smoothie_type, check_info_presence, remove_extra_newline, damage_elemental_emojis


# returns dictionary of extracted information for an input object, or error codes if an error occurs
def get_object_info(search_query):

	# check for status effect or modifier first
	modifier_info = get_modifier_info(search_query)
	if modifier_info is not None:
		return modifier_info

	search_query, smoothie_type = detect_smoothie_type(search_query)
	result = locate_object_url(search_query)

	if result is None:  # unable to locate URL for item
		return 101
	elif not result:  # Google API daily resource exhausted
		return 103
	elif isinstance(result, str):
		page_content, page_title = get_page_data(result, True)
	else:
		page_content, page_title = result[0], result[1]

	try:
		object_info = get_infobox_info(page_content)
	except:
		# page layout not supported
		return (102, page_title)

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


# returns a formatted string, displaying the extracted object information in a presentable format
def format_object_info(object_info):
	formatted_string = f"**Name:** {object_info['name']}\n"

	if 'description' in object_info:
		formatted_string += f"**Description:** {object_info['description']}\n"
	if 'category' in object_info:
		formatted_string += f"**Category:** {object_info['category']}\n\n"

	# status effects / mutations
	if 'source' in object_info:
		formatted_string += f"\n**Source:**\n{object_info['source']}\n"

	# resource nodes
	if 'brokenwith' in object_info:
		formatted_string += f"**Harvest With:** {damage_elemental_emojis(object_info['brokenwith'])}\n"

	# characters
	if 'species' in object_info:
		formatted_string += f"**Species:** {object_info['species']}\n"
	if 'gender' in object_info:
		formatted_string += f"**Gender:** {object_info['gender']}\n"

	# creatures
	if 'aggression' in object_info:
		formatted_string += f"**Aggression:** {object_info['aggression']}\n\n"
	if 'tier' in object_info:
		# some creatures don't have tiers, e.g. harmless
		formatted_string = remove_extra_newline(formatted_string) + f"**Tier:** {object_info['tier']}\n\n"
	if 'tamewith' in object_info:
		formatted_string += f"**Tamed With:** {object_info['tamewith']}\n"

	if 'effectresistance' in object_info:
		# effect resistance seems to have been removed from the creature infoboxes after arrival of bestiary
		formatted_string += f"**Effect Resistance:** {object_info['effectresistance']}\n"
	if 'resistance' in object_info:
		formatted_string += f"**Dmg. Resistance:** {damage_elemental_emojis(object_info['resistance'])}\n"
	if 'eresistance' in object_info:
		formatted_string += f"**Elem. Resistance:** {damage_elemental_emojis(object_info['eresistance'])}\n"
	if 'weakness' in object_info:
		formatted_string += f"**Dmg.  Weakness:** __{damage_elemental_emojis(object_info['weakness'])}__\n".replace(', ', '__, __')
	if 'eweakness' in object_info:
		formatted_string += f"**Elem.  Weakness:** __{damage_elemental_emojis(object_info['eweakness'])}__\n".replace(', ', '__, __')
	if 'weakpoint' in object_info:
		formatted_string += f"**Weak Point:** __{object_info['weakpoint']}__\n"

	if 'loot' in object_info:
		# if no optional fields, remove extra newline added from above
		formatted_string = remove_extra_newline(formatted_string) + f"\n**Loot:**\n{object_info['loot']}"

	# building structures
	if 'sturdiness' in object_info:
		formatted_string += f"**Sturdiness:** {object_info['sturdiness']}\n"
	if 'weight' in object_info:
		formatted_string += f"**Weight:** {object_info['weight']}\n"

	# consumables
	if 'food' in object_info:
		# account for special cases of food with Fresh versions
		formatted_string += f"**Food:** {object_info['food'].replace(')+', '); +')}\n"
	if 'water' in object_info:
		formatted_string += f"**Water:** {object_info['water']}\n"
	if 'health' in object_info:
		formatted_string += f"**Health:** {object_info['health']}\n"

	# armor
	if 'class' in object_info:
		formatted_string += f"**Armor Class:** {object_info['class']}\n"
	if 'defense' in object_info:
		formatted_string += f"**Defense:** {object_info['defense']}\n"

	# tools
	if 'tooltype' in object_info:
		formatted_string += f"**Damage Type:** {damage_elemental_emojis(object_info['tooltype'])}\n"
	if 'augmenttype' in object_info:
		formatted_string += f"**Elemental Type:** {damage_elemental_emojis(object_info['augmenttype'])}\n"
	if 'damage' in object_info:
		formatted_string += f"**Damage:** {object_info['damage']}\n"
	if 'stun' in object_info:
		formatted_string += f"**Stun:** {object_info['stun']}\n"
	if 'speed' in object_info:
		formatted_string += f"**Speed:** {object_info['speed']}\n"

	if 'effects' in object_info:
		formatted_string += f"**Effects:** {', '.join(object_info['effects'])}\n"
	if 'upgradeeffect' in object_info:
		formatted_string += f"**Sleek Upgrade Effect:** {object_info['upgradeeffect']}\n"

	if 'recipe' in object_info:
		formatted_string = remove_extra_newline(formatted_string) + f"\n**Recipe:** {object_info['recipe_name']}\n"

		for item in sorted(object_info['recipe'].items()):
			formatted_string += f"{item[1]} {item[0]}\n"

	if 'repair_cost' in object_info:
		formatted_string = remove_extra_newline(formatted_string) + f"\n**Repair Cost:**\n"

		for item in sorted(object_info['repair_cost'].items()):
			formatted_string += f"{item[1]} {item[0]}\n"

	return formatted_string
