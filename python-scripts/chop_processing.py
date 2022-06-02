from math import ceil
from collections import Counter
from re import findall, IGNORECASE

from object_search import *
from global_variables import *


# returns a Counter containing processed item names as keys and their quantities
def process_chop_input(user_input, allow_numberless=False):

	# regex search patterns
	name_pattern = "[a-z _+'?-]+"
	qty_pattern = '[0-9]+'
	regex_pattern = f'{name_pattern} {qty_pattern}|{qty_pattern} {name_pattern}'

	# toggle recognition of comma-separated item names without any quantities
	if allow_numberless:
		regex_pattern += f'|{name_pattern}'

	# find all item-quantity pairs
	results = findall(regex_pattern, user_input, IGNORECASE)
	processed_input = Counter()

	for item in results:
		item = item.split()

		# ignore items with input quantity of 0
		if '0' in item:
			continue

		# set default quantity of -1 for items with no specified quantity
		item_qty = -1
		if item[0].isdecimal():  # quantity came before item name
			item_qty = item.pop(0)
		elif item[-1].isdecimal():  # quantity came after item name
			item_qty = item.pop(-1)

		item_name = ' '.join(item)
		processed_input[item_name] += int(item_qty)

	return processed_input


# checks if item is valid for Chopping List
# returns True if a given item fulfils a given condition, otherwise False
def check_valid_item(item_info, mode=0):
	condition_1 = item_info['name'] in SPECIAL_ITEMS
	condition_2 = 'category' in item_info and item_info['category'] == 'Natural Resources'
	condition_3 = 'recipe' in item_info

	if mode == 1:  # check against conditions 1 and 2 only
		condition_3 = False
	elif mode == 2:  # check against condition 3 only
		condition_1, condition_2 = False, False

	return condition_1 or condition_2 or condition_3


# recursive function to break an item down to its base components and update Chopping List quantities
# returns rolling Counter by default, also returns overall item name and quantity if it is the original function call
def process_chop_components(item_name, quantity, base_components=None):
	if base_components is None:
		base_components = Counter()
		originalCall = True
	else:
		originalCall = False

	item_info = process_object_input(item_name)

	if not isinstance(item_info, dict):
		if originalCall:  # return any errors if they occur for a user-inputted item
			return item_info

		else:  # print warning if any errors occur for component materials
			print(f"WARNING: Error {item_info} occurred for component material '{item_name}'.\n")
			return base_components

	item_name = item_info['name']

	# stop recursion if item is natural resource, or in SPECIAL_ITEMS
	if check_valid_item(item_info, 1):
		base_components[item_name] += quantity

	elif check_valid_item(item_info, 2):
		recipe_quantity = re.findall('x\d+', item_info['recipe_name'])

		if recipe_quantity:
			# remove letter x and convert quantity to integer
			recipe_quantity = int(recipe_quantity[0][1:])
		else:
			recipe_quantity = 1

		# calculate number of times to craft the recipe
		crafting_count = ceil(quantity / recipe_quantity)

		recipe = item_info['recipe']

		# multiply item costs by quantity
		for material in recipe:
			recipe[material] *= crafting_count

			# recursively run function on component materials
			base_components = process_chop_components(material, recipe[material], base_components)

		# calculate actual number of items produced, not the number of times the recipe is used (i.e. recipes which produce multiple items)
		quantity = recipe_quantity * crafting_count

	# return error 105 if overall object is not a resource or craftable item, e.g. creature
	elif originalCall:
		return [105, item_name]

	# return only the material Counter if function was recursively called
	if not originalCall:
		return base_components

	# return smoothie name with prefixed base type
	if 'category' in item_info and 'smoothie' in item_info['category'].lower():
		item_name = item_info['recipe_name']

	return item_name, quantity, base_components
