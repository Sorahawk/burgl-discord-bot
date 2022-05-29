from math import ceil
from collections import Counter
from re import findall, IGNORECASE

from object_search import *
from dynamodb_methods import *
from global_variables import *


# returns a Counter containing processed item names as keys and their quantities
def process_chop_input(user_input):

	# regex search patterns
	name_pattern = "[a-z _+'?-]+"
	qty_pattern = '[0-9]+'
	regex_pattern = f'{name_pattern} {qty_pattern}|{qty_pattern} {name_pattern}'

	# find all item-quantity pairs
	results = findall(regex_pattern, user_input, IGNORECASE)
	processed_input = Counter()

	for item in results:
		item = item.split()

		if item[0].isdecimal():  # quantity came before item name
			item_qty = item.pop(0)
		else:  # quantity came after item name
			item_qty = item.pop(-1)

		item_name = ' '.join(item)
		processed_input[item_name] += int(item_qty)

	return processed_input


# recursive function to break an item down to its base components and update Chopping List quantities
# returns rolling Counter to itself by default
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
	if item_name in SPECIAL_ITEMS or ('category' in item_info and item_info['category'] == 'Natural Resources'):
		base_components[item_name] += quantity

	elif 'recipe' in item_info:
		recipe = item_info['recipe']

		if 'recipe_name' not in item_info:
			item_info['recipe_name'] = ''

		recipe_quantity = re.findall('x\d+', item_info['recipe_name'])

		if recipe_quantity:
			# remove letter x and convert quantity to integer
			recipe_quantity = int(recipe_quantity[0][1:])

			# round up desired quantity to the nearest number divisible by recipe quantity
			quantity = ceil(quantity / recipe_quantity)
		else:
			recipe_quantity = 1

		# multiply item costs by quantity
		for material in recipe:
			recipe[material] *= quantity

			# recursively run function on component materials
			base_components = process_chop_components(material, recipe[material], base_components)

		quantity *= recipe_quantity

	# return error 105 if object is not a resource or craftable item, e.g. creature
	else:
		return [105, item_name]

	if not originalCall:
		return base_components

	# return smoothie name with prefixed base type
	if 'category' in item_info and 'smoothie' in item_info['category'].lower():
		item_name = item_info['recipe_name']

	return item_name, quantity, base_components
