
# dictionary of all the possible Discord statuses for the bot
# use the activity as the key since the ActivityType might not be unique
# if ActivityType is streaming, then second item in corresponding tuple is for URL
# ActivityType 0 is gaming, 1 is streaming, 2 is listening, 3 is watching, 4 is custom, 5 is competing
ACTIVITY_STATUSES = {'with a pet aphid': (0, ), 'with a pet weevil': (0, ),

					'data to Dr. Tully': (1, 'https://www.youtube.com/watch?v=aueMEZC8uDE'),
					'broodmother trials': (1, 'https://www.youtube.com/watch?v=tZlcSr5DfRI'),

					'the ladybugs cooing': (2, ), 'audio logs': (2, ),

					'the backyard': (3, ), 'the teens': (3, ), 'the Watcher': (3, ), 'the fungus spread': (3, ),

					'burger flipping': (5, )}


# string of the base wiki URL
BASE_WIKI_URL = 'https://grounded.fandom.com/wiki/'


# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'


# dictionary of bot commands, keys are the exact names of the corresponding methods
# add a whitespace behind the commands so it won't recognise invalid commands, e.g. .helpp
BOT_COMMAND_LIST = {'help_method': f'{BOT_COMMAND_PREFIX}help ', 'search_method': f'{BOT_COMMAND_PREFIX}search ',
					'card_method': f'{BOT_COMMAND_PREFIX}card ', 'bind_method': f'{BOT_COMMAND_PREFIX}bind ',
					'purge_method': f'{BOT_COMMAND_PREFIX}purge '}


# dictionary of command flags
BOT_COMMAND_FLAGS = {'force_search': ' -f ', 'modifier': ' -m '}


# list of formatted strings to display as help message
BOT_HELP_MESSAGE = [f"**`{BOT_COMMAND_LIST['help_method']}`**\nDisplays this list.",

				f"**`{BOT_COMMAND_LIST['search_method']}<object_name>`**\nDisplays any available details of the object. Works with most things, e.g. creatures, resources, equipment, building components.\n"\
				"*Use flag `-m` to search for status effects or mutations.\nUse flag `-f` to force the search to bypass any binded shortcuts.*",

				f"**`{BOT_COMMAND_LIST['card_method']}<creature_name>`**\nDisplays the specified creature's bestiary card.\n"\
				"*Use flag `-f` to force the search to bypass any binded shortcuts.*",

				f"**`{BOT_COMMAND_LIST['bind_method']}<full_object_name>, <shortcut_1>, <shortcut_2>, ...`**\nBinds one or more shortcut phrases to a full object name.\n*Each parameter is case-insensitive and must be separated by a comma.*",

				f"**`{BOT_COMMAND_LIST['purge_method']}`**\nPurges the webpage data and object information caches."]


# dictionary of custom server emojis
CUSTOM_EMOJIS = {'BURG.L': '<:BURGL_Icon:970544869124755467>', 'Fresh': '<:ElementalType_Fresh:970550878966796308>',
				'Salty': '<:ElementalType_Salty:970550879226847302>', 'Spicy': '<:ElementalType_Spicy:970551950405947453>',
				'Busting': '<:DamageType_Busting:970552005250646036>', 'Chopping': '<:DamageType_Chopping:970552005883998269>',
				'Digging': '<:DamageType_Digging:970552065577328650>', 'Explosive': '<:DamageType_Explosive:970552089493262346>',
				'Slashing': '<:DamageType_Slashing:970552106496978964>', 'Stabbing': '<:DamageType_Stabbing:970552122548559872>',
				'Aphid': '<:Pet_Aphid:973157551141158962>', 'Weevil': '<:Pet_Weevil:973157551279575111>'}


# DynamoDB table names as strings, and a dictionary of their corresponding key and attribute headers
SHORTCUT_STORAGE = 'ShortName-FullName'
OBJECT_INFO_CACHE = 'SearchQuery-ObjectInfo'
PAGE_HTML_CACHE = 'WikiURL-PageHTML'

DDB_TABLE_HEADERS = {SHORTCUT_STORAGE: ('short_name', 'full_name'),
					OBJECT_INFO_CACHE: ('search_query', 'object_info'),
					PAGE_HTML_CACHE: ('wiki_url', 'page_html')}


# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 970882023055036426


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_API = 0.35


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_CARD = 0.75


# dictionary of smoothie bases and their base ingredients
SMOOTHIE_BASES = {'basic': 'Grub Goop', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}
