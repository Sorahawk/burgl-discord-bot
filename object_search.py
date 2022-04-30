from object_search_functions import *
from helper_functions import prefix_zero, remove_extra_newline


# retrieve details for an object
def get_object_info(search_query):
	SPECIAL_SMOOTHIE_TYPES = {'beefy': 'Health recovery x2', 'sticky': 'Effect duration x2'}

	# detect any special smoothie types from input, e.g. beefy, sticky
	for special in SPECIAL_SMOOTHIE_TYPES:
		if special in search_query.lower():
			new_search_query = re.compile(special, re.IGNORECASE).sub('', search_query).strip()

			# if the input was just the smoothie type alone, do not remove it
			if new_search_query:
				search_query = new_search_query
				smoothie_type = special

			break

	print(search_query)


	url = locate_object_url(search_query)

	if url is None:  # unable to locate URL for item
		return 101
	elif not url:  # Google API daily resource exhausted
		return 103

	page_title, page_content = get_page_data(url)

	try:
		object_info = get_infobox_info(page_content)
	except:
		# page layout not supported
		return (102, page_title)

	has_recipe, has_repair_cost = check_info_presence(page_content)

	if has_recipe:
		try:
			object_info['recipe'], object_info['recipe_name'] = get_recipe_table(page_content, object_info['name'])
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


# converts extracted object information into a formatted string
def format_object_info(object_info):
	formatted_string = f"**Name:** {object_info['name']}\n"

	if 'description' in object_info:
		formatted_string += f"**Description:** {object_info['description']}\n"
	if 'category' in object_info:
		formatted_string += f"**Category:** {object_info['category']}\n\n"

	# resource nodes
	if 'brokenwith' in object_info:
		formatted_string += f"**Harvest With:** {object_info['brokenwith']}\n"

	# characters
	if 'species' in object_info:
		formatted_string += f"**Species:** {object_info['species']}\n"
	if 'gender' in object_info:
		formatted_string += f"**Gender:** {object_info['gender']}\n"

	# creatures
	if 'aggression' in object_info:
		# account for special case where Bee has 'NeutralAggressive'
		formatted_string += f"**Aggression:** {object_info['aggression'].replace('lA', 'l; A')}\n\n"
	if 'tier' in object_info:
		# tier does not show up for all creatures, e.g. harmless
		formatted_string = remove_extra_newline(formatted_string) + f"**Tier:** {object_info['tier']}\n\n"

	if 'tamewith' in object_info:
		formatted_string += f"**Tamed With:** {object_info['tamewith']}\n"
	if 'effectresistance' in object_info:
		formatted_string += f"**Resistance (Effect):** {object_info['effectresistance']}\n"
	if 'resistance' in object_info:
		formatted_string += f"**Resistance (Damage):** {object_info['resistance']}\n"
	if 'eresistance' in object_info:
		formatted_string += f"**Resistance (Elemental):** {object_info['eresistance']}\n"
	if 'weakness' in object_info:
		formatted_string += f"**Weakness (Damage):** __{object_info['weakness']}__\n"
	if 'eweakness' in object_info:
		formatted_string += f"**Weakness (Elemental):** __{object_info['eweakness']}__\n"
	if 'weakpoint' in object_info:
		formatted_string += f"**Weak Point:** __{object_info['weakpoint']}__\n"

	if 'loot' in object_info:
		# if no optional fields, remove extra newline added from aggression
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
		formatted_string += f"**Damage Type:** {object_info['tooltype']}\n"
	if 'augmenttype' in object_info:
		formatted_string += f"**Element Type:** {object_info['augmenttype']}\n"
	if 'damage' in object_info:
		formatted_string += f"**Damage:** {prefix_zero(object_info['damage'])}\n"
	if 'stun' in object_info:
		formatted_string += f"**Stun:** {prefix_zero(object_info['stun'])}\n"
	if 'speed' in object_info:
		formatted_string += f"**Speed:** {prefix_zero(object_info['speed'])}\n"

	if 'effects' in object_info:
		formatted_string += f"**Effects:** {', '.join(object_info['effects'])}\n"

	if 'recipe' in object_info:
		formatted_string = remove_extra_newline(formatted_string) + f"\n**Recipe:** {object_info['recipe_name']}\n"

		for item in sorted(object_info['recipe'].items()):
			formatted_string += f"{item[1]} {item[0]}\n"

	if 'repair_cost' in object_info:
		formatted_string = remove_extra_newline(formatted_string) + f"\n**Repair Cost:**\n"

		for item in sorted(object_info['repair_cost'].items()):
			formatted_string += f"{item[1]} {item[0]}\n"

	return formatted_string
