from url_processing import *
from global_constants import *


# extracts the weakness tables from the wiki, processing them into a single dictionary for return
def weakness_extraction():
	url = f'{BASE_WIKI_URL}Creature_Strengths_and_Weaknesses'
	page_content = get_page_data(url)

	tables = page_content.find_class('wds-is-current')

	elemental_table = tables[1]
	damage_table = tables[3]

	weakness_dict = {}
	weakness_dict = process_weakness_table(elemental_table, weakness_dict)
	weakness_dict = process_weakness_table(damage_table, weakness_dict)

	return weakness_dict


# processes a given weakness table into a given dictionary
def process_weakness_table(weakness_table, weakness_dict):
	weakness_table = weakness_table.xpath('table/tbody/tr')
	weakness_types = weakness_table[1].xpath('th')
	creatures = weakness_table[2].xpath('td')

	for column in range(len(weakness_types)):
		# store weakness types as lowercase
		weakness = weakness_types[column].text_content().strip().lower()

		creature_list = []

		for creature_name in creatures[column].itertext():
			if creature_name.strip():
				creature_list.append(creature_name.strip())

		weakness_dict[weakness] = creature_list.sort()

	return weakness_dict
