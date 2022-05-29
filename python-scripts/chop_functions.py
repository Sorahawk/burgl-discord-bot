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


# recursive function to break an item down to its base components and update chopping list quantities
# returns rolling Counter to itself by default
def process_chop_components(item, quantity, base_components=None):
	item_info = process_object_input(item)

	if not isinstance(item_info, dict):
		if base_components is None:  # return any errors if they occur for a user-inputted item
			return item_info

		else:  # print warning if any errors occur for component materials
			print(f"WARNING: Error {item_info} occurred for component material '{item}'.\n")
			return base_components

	if not base_components:
		base_components = Counter()

	item_name = item_info['name']
	recipe_quantity = 1

	# only insert an item into chopping list if it is in SPECIAL_ITEMS, or if it is a natural resource
	if item_name in SPECIAL_ITEMS or ('category' in item_info and item_info['category'] == 'Natural Resources'):
		table_name = CHOPPING_LIST

		# check if material already exists in the chopping list
		existing_quantity = ddb_retrieve_item(table_name, item_name)

		total_quantity = quantity
		if existing_quantity:
			total_quantity += int(existing_quantity['quantity'])

		if ddb_insert_item(table_name, item_name, total_quantity):
			base_components[item_name] += quantity

	elif 'recipe' in item_info:
		recipe = item_info['recipe']

		if 'recipe_name' in item_info:
			recipe_quantity = re.findall('x\d+', item_info['recipe_name'])

			if recipe_quantity:
				# convert quantity to integer
				recipe_quantity = int(recipe_quantity[0][1:])

				# round up desired quantity to the nearest number divisible by recipe quantity
				quantity = ceil(quantity / recipe_quantity)
			else:
				recipe_quantity = 1

		# multiply item costs by quantity
		for material in recipe.keys():
			recipe[material] *= quantity

			# recursively run function on component materials
			base_components = process_chop_components(material, recipe[material], base_components)

	# return error 105 if object is not a resource or craftable item, e.g. creature
	else:
		return [105, item_name]

	# return the full name of item being crafted
	if 'recipe_name' in item_info and item_info['recipe_name']:
		# remove recipe quantity from recipe name
		base_components['name'] = ' '.join(item_info['recipe_name'].split()[:-1])
	else:
		base_components['name'] = item_name

	# update final quantity since some recipes need the desired quantity to be rounded up
	base_components['quantity'] = quantity * recipe_quantity
	return base_components
