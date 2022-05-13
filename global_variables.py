
# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 970882023055036426


# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'


# list of bot commands
BOT_COMMAND_LIST = ['help', 'search', 'card', 'bind', 'purge']


# dictionary of command flags, can only be one letter, following a dash
BOT_COMMAND_FLAGS = {'force_search': '-f', 'modifier': '-m'}


# list containing lists of strings to populate the embedded help menu
BOT_HELP_MESSAGE = [['**`.help`**', 'Displays this menu.'],

					['**`.search <object_name>`**', 'Displays any available details of the object. Works with most things, e.g. creatures, resources, equipment, building components.',
						'*Use flag `-m` to search for status effects or mutations.*', '*Use flag `-f` to force the search to bypass any binded shortcuts.*'],

					['**`.card <creature_name>`**', "Displays the specified creature's bestiary card.",
						'*Use flag `-f` to force the search to bypass any binded shortcuts.*'],

					['**`.bind <full_object_name>, <shortcut_1>, <shortcut_2>, ...`**', 'Binds one or more shortcut phrases to a full object name.',
						'*Each parameter is case-insensitive and must be separated by a comma.*'],

					['**`.purge`**', 'Purges the webpage data and object information caches.']]


# dictionary of typical messages used by the bot, including warning and error messages
BOT_VOICELINES = {'hello': 'Hello there! Acting science manager B-B-B-BURG.L at your service!', 'purged': 'Data caches have been purged.',
				'empty': 'Please provide input parameters.', 'insufficient': 'A minimum of two comma-separated parameters are required.',
				101: "**ERROR 101:** Unable to locate 'VAR1'. Try typing in the object's full name.", 102: "**ERROR 102:** Wiki page for 'VAR1' has an unsupported layout.",
				103: '**ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.', 104: "**ERROR 104:** Unable to locate Creature Card for 'VAR1'. Type in the exact name of the creature."}


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


# dictionary of custom server emojis
CUSTOM_EMOJIS = {'BURG.L': '<:BURGL_Icon:970544869124755467>', 'Fresh': '<:ElementalType_Fresh:970550878966796308>',
				'Salty': '<:ElementalType_Salty:970550879226847302>', 'Spicy': '<:ElementalType_Spicy:970551950405947453>',
				'Busting': '<:DamageType_Busting:970552005250646036>', 'Chopping': '<:DamageType_Chopping:970552005883998269>',
				'Digging': '<:DamageType_Digging:970552065577328650>', 'Explosive': '<:DamageType_Explosive:970552089493262346>',
				'Slashing': '<:DamageType_Slashing:970552106496978964>', 'Stabbing': '<:DamageType_Stabbing:970552122548559872>',
				'Aphid': '<:Pet_Aphid:973157551141158962>', 'Weevil': '<:Pet_Weevil:973157551279575111>'}


# string of the base wiki URL
BASE_WIKI_URL = 'https://grounded.fandom.com/wiki/'


# dictionary of smoothie bases and their base ingredients
SMOOTHIE_BASES = {'basic': 'Grub Goop', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_API = 0.35


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_CARD = 0.75


# DynamoDB table names as strings, and a dictionary of their corresponding key and attribute headers
SHORTCUT_STORAGE = 'ShortName-FullName'
OBJECT_INFO_CACHE = 'SearchQuery-ObjectInfo'
PAGE_HTML_CACHE = 'WikiURL-PageHTML'

DDB_TABLE_HEADERS = {SHORTCUT_STORAGE: ('short_name', 'full_name'),
					OBJECT_INFO_CACHE: ('search_query', 'object_info'),
					PAGE_HTML_CACHE: ('wiki_url', 'page_html')}
