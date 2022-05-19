
# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 970882023055036426


# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'


# list of bot commands
BOT_COMMAND_LIST = ['help', 'search', 'card', 'bind', 'purge', 'clear']


# dictionary of command flags
# each flag can only be a single letter
BOT_COMMAND_FLAGS = {'delete_binding': 'd', 'force_search': 'f', 'get_gold': 'g', 'view_bindings': 'v'}


# list containing lists of strings to populate the embedded help menu
BOT_HELP_MESSAGE = [
	['**.help**', 'Displays this help menu.'],

	['**.search <object_name>**', 'Displays any available details of the object. Works with most things, e.g. creatures, resources, equipment, building components.',
		'*+Use flag `-f` to force the search to bypass any binded shortcuts.*'],

	['**.card <creature_name>**', "Displays the specified creature's bestiary card.",
		"*+Use flag `-g` to display the creature's gold bestiary card.*", '*+Use flag `-f` to force the search to bypass any binded shortcuts.*'],

	['**.bind <object_name>, <shortcut_1>, [shortcut_2], ...**', 'Binds an object name to one or more shortcut phrases.',
		'*+Use flag `-v` to view all binded shortcuts (no arguments required).*', '*+Use flag `-d` to delete shortcuts for specified objects (at least one object_name required).*',
		'*+Each parameter is case-insensitive and must be separated by a comma.*'],

	['**.purge**', 'Purges the webpage data and object information caches.'],

	['**.clear**', 'Clears up to 100 recent messages (in server channels), and all bot messages (in private chats).']
]


# dictionary of typical messages used by the bot, including warning and error messages
BOT_VOICELINES = {
	'hello': 'Hello there! Acting science manager B-B-B-BURG.L at your service!',
	'debug': 'My data caches are missing!',
	'purged': 'Data caches have been purged.',
	'empty': 'Please provide input parameters.',
	'insufficient': 'A minimum of two comma-separated parameters are required.',
	'invalid_bind': 'Specified bindings not found.',
	'embed_close': 'Menu has been closed.',

	101: "**ERROR 101:** Unable to locate 'VAR1'. Try typing in the object's full name.",
	102: "**ERROR 102:** Wiki page for 'VAR1' has an unsupported layout.",
	103: '**ERROR 103:** Google API daily limit exceeded. Type in the exact name of the object.',
	104: "**ERROR 104:** Unable to locate Creature Card for 'VAR1'. Type in the exact name of the creature."
}


# dictionary of the available Discord statuses for the bot
# if activity (key) is meant to be a 'Streaming' activity, then corresponding value is a string URL
# otherwise corresponding value is the respective ActivityType

# available ActivityTypes: 0 is gaming (Playing), 1 is streaming (Streaming), 2 is listening (Listening to),
# 3 is watching (Watching), 4 is custom, 5 is competing (Competing in)
ACTIVITY_STATUSES = {
	'with a pet aphid': 0,
	'with a pet weevil': 0,
	'the ladybugs cooing': 2,
	'audio logs': 2,
	'the backyard': 3,
	'the teens': 3, 'the Watcher': 3,
	'the fungus spread': 3,
	'burger flipping': 5,
	'data to Dr. Tully': 'https://www.youtube.com/watch?v=aueMEZC8uDE',
	'broodmother trials': 'https://www.youtube.com/watch?v=tZlcSr5DfRI'
}


# dictionary of custom emojis
CUSTOM_EMOJIS = {
	'LeftArrow': '◀️',
	'RightArrow': '▶️',
	'CrossMark': '❎',

	'BURG.L': '<:BURGL_Icon:976155200102486016>',

	'Aphid': '<:Pet_Aphid:975803016735256677>',
	'Weevil': '<:Pet_Weevil:975803016819146842>',

	'Light': '<:ArmorClass_Light:976063426470244382>',
	'Medium': '<:ArmorClass_Medium:976063426575097856>',
	'Heavy': '<:ArmorClass_Heavy:976063426600243250>',

	'Fresh': '<:ElementalType_Fresh:976063714807652353>',
	'Spicy': '<:ElementalType_Spicy:976063715302588426>',
	'Salty': '<:ElementalType_Salty:976063715017392188>',
	'Sour': '<:ElementalType_Sour:976063714702802945>',

	'Busting': '<:DamageType_Busting:976155517707763762>',
	'Chopping': '<:DamageType_Chopping:976155517699383297>',
	'Digging': '<:DamageType_Digging:976155517670002788>',
	'Explosive': '<:DamageType_Explosive:976155517690982470>',
	'Slashing': '<:DamageType_Slashing:976155517363830835>',
	'Stabbing': '<:DamageType_Stabbing:976155517766496286>',
	'Repair': '<:DamageType_Repair:976155517770682428>',

	'Eyes': '<:WeakPoint_Eyes:976063745233141791>',
	'Back': '<:WeakPoint_Back:976063745363161128>',
	'Gut': '<:WeakPoint_Gut:976063745279279104>',
	'Legs': '<:WeakPoint_Legs:976063745245716500>',
	'Rump': '<:WeakPoint_Rump:976063744897593387>',
	'RobotBack': '<:WeakPoint_RobotBack:976063745266704394>'
}


# dictionary of object info attributes that do not require any processing of values
# each entry includes the index of the field in the embed which they should be inserted at
# if the attribute has a special name, the content for that entry is stored in a tuple
# first item in the tuple is index, and second item is special name
OBJECT_INFO_ATTRIBUTES = {
	'aggression': 1,
	'category': 1,
	'species': 1,
	'source': (1, 'Source(s)'),

	'tier': 2,
	'gender': 2,

	'tamewith': (3, 'Tame with'),

	'damage': 4,
	'food': 4,
	'sturdiness': 4,

	'stun': 5,
	'defense': 5,
	'water': 5,
	'weight': 5,

	'effectresistance': (6, 'Effect Resistance'),
	'speed': 6,
	'health': 6,

	'effects': 7,

	'upgradeeffect': (8, 'Sleek Upgrade Effect'),

	'loot': 10
}


# string of the base wiki URL
BASE_WIKI_URL = 'https://grounded.fandom.com/wiki/'


# dictionary of smoothie bases and their base ingredients
SMOOTHIE_BASES = {'basic': 'Grub Goop', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}


# list of words which have atypical capitalisation, excluding robot and device names like BURG.L or TAYZ.T
SPECIAL_NAMES = ['AARTZ', 'BBQ', 'BLT', 'EverChar', 'de', 'of', 'on', 'the']


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_API = 0.35


# sets the minimum threshold of similarity between search query and predicted result
SIMILAR_THRESHOLD_CARD = 0.75


# DynamoDB table names as strings, and a dictionary of their corresponding key and attribute headers
SHORTCUT_STORAGE = 'ShortName-FullName'
OBJECT_INFO_CACHE = 'SearchQuery-ObjectInfo'
PAGE_HTML_CACHE = 'WikiURL-PageHTML'

DDB_TABLE_HEADERS = {
	SHORTCUT_STORAGE: ('short_name', 'full_name'),
	OBJECT_INFO_CACHE: ('search_query', 'object_info'),
	PAGE_HTML_CACHE: ('wiki_url', 'page_html')
}


# max number of fields per embed page when viewing binded shortcuts
MAX_EMBED_FIELDS = 15
