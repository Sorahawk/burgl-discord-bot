
### LINUX ###

# absolute path to the project folder on the Linux cloud instance
# cannot use os.getcwd() because systemd service runs the script from root directory
LINUX_ABSOLUTE_PATH = '/home/ubuntu/burgl-discord-bot/python-scripts'

# name of the bot service running on the Linux cloud instance
LINUX_SERVICE_NAME = 'burgl-bot.service'



### DISCORD ###

# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 976308922010959892

# main channel object, to be initialised when the bot calls on_ready()
MAIN_CHANNEL = None

# list of elevated Discord roles
ELEVATED_USER_ROLES = [981223991547158609, 886572468012199967]

# Discord server role name to ping for notifications
NOTIFY_ROLE_NAME = '<@&981223991547158609>'



### AMAZON WEB SERVICES ###

# name of AWS region in use
AWS_REGION_NAME = 'ap-southeast-1'

# DynamoDB table names as strings, and a dictionary of their corresponding key and attribute headers
SHORTCUT_TABLE = 'Shortcut_Storage'
INFO_TABLE = 'ObjectInfo_Cache'
HTML_TABLE = 'PageHTML_Cache'
CHOPPING_TABLE = 'ChoppingList_Storage'
TASK_TABLE = 'TaskScheduler_Storage'
MISC_TABLE = 'Miscellaneous_Storage'

TABLE_HEADERS = {
	SHORTCUT_TABLE: ('short_name', 'full_name'),
	INFO_TABLE: ('search_query', 'object_info'),
	HTML_TABLE: ('wiki_url', 'page_html'),
	CHOPPING_TABLE: ('item_name', ('quantity', 'components')),
	TASK_TABLE: ('task_id', 'task_description'),
	MISC_TABLE: ('variable_name', 'variable_value')
}



### GITHUB ###

# URL of the project GitHub repository
REPOSITORY_URL = 'https://api.github.com/repos/Sorahawk/burgl-discord-bot/commits'

# dictionary to store latest headers of project repository on GitHub
REPOSITORY_HEADERS = {}



### STEAM ###

# dictionary to store latest timestamps of changes from Steam
STEAM_TIMESTAMPS = {}

# list of Steam development branch names whose activity will notify users
NOTIFY_BRANCHES = ['buddha', 'public', 'public_test']



### MAIN ###

# object instance of the bot itself, to be set after initialisation in bot_main
BOT_INSTANCE = None

# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'

# list of bot commands
BOT_COMMAND_LIST = ['search', 'card', 'bind', 'chop', 'todo', 'help', 'clear', 'purge', 'sleep']

# dictionary of command flags
# each flag can only be a single letter
BOT_COMMAND_FLAGS = {'delete': 'd', 'edit': 'e', 'find': 'f', 'gold': 'g', 'override': 'o', 'reset': 'r', 'view': 'v'}

# logger object to be instantiated at initialisation
OPERATIONS_LOG = None

# color code for Embed messages
# 0x6542E1 is the purple that BURG.L's icon has in-game while speaking
EMBED_COLOR_CODE = 0x6542E1

# max number of fields per embed page when viewing binded shortcuts
MAX_SHORTCUT_FIELDS = 15

# max number of items per command entry when entering items into the Chopping List
MAX_CHOPPING_INPUT = 9

# max number of fields per embed page when viewing the Chopping List
MAX_CHOPPING_FIELDS = 10

# max number of fields per embed page when viewing the Task Scheduler
MAX_TODO_FIELDS = 10

# max number that can be used to generate task IDs
MAXIMUM_ID = 999

# list of valid to-do priority levels for Task Scheduler
TODO_PRIORITY_LEVELS = ['Low', 'Medium', 'High', 'Recurring']

# template format for harvesting task descriptions
HARVEST_DESCRIPTION_TEMPLATE = '[Chop] Harvest VAR1 VAR2'

# dictionary to act as a global reference table linking harvesting task materials to their task IDs
# to be populated during runtime
HARVEST_TASK_REFERENCE = {}

# decimal value for minimum ratio of string similarity between search query and predicted result
SIMILAR_THRESHOLD_API = 0.35

# decimal value for minimum ratio of string similarity between search query and predicted result
SIMILAR_THRESHOLD_CARD = 0.75

# integer value of local timezone offset with respect to UTC
TIMEZONE_OFFSET = 8

# integer value for day of the week to conduct weekly cache clear
# 0 is Monday, 6 is Sunday
CACHE_CLEAR_DAY = 0

# integer value for hour of the day to conduct weekly cache clear
# 0 is 12AM, 23 is 11PM
CACHE_CLEAR_HOUR = 6

# base URL for the Grounded Wiki
BASE_WIKI_URL = 'https://grounded.fandom.com/wiki/'

# name of the generic smoothie
DEFAULT_SMOOTHIE_NAME = 'Questionable Slop'

# dictionary of smoothie bases and their base ingredients
SMOOTHIE_BASES = {'basic': 'Grub Sludge', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}

# list of words which have atypical capitalisation
SPECIAL_WORDS = ['AARTZ', 'BBQ', 'BLT', 'BURG.L', 'EverChar', 'HQ', 'a', 'and', 'at', 'as well as', 'de', 'is', 'of', 'on', 'the', 'to']

# lists of words that correspond to each armor piece type
ARMOR_HEAD = ['face', 'goggles', 'hat', 'head', 'helmet', 'hood', 'mask']
ARMOR_UPPER_BODY = ['arm', 'chest', 'poncho', 'shirt', 'shoulder', 'torso', 'vest']
ARMOR_LOWER_BODY = ['boots', 'knee', 'leg', 'pants', 'shin', 'shoes']


# dictionary containing nested lists of strings to populate the help menu, categorised by command type
BOT_HELP_MENU = {
	'Main': [
		['.search <object_name>', 'Displays any available information of the object. Works with most things, e.g. creatures, resources, equipment, building components.',
		'+Use flag `-o` to override any binded shortcuts.'],

		['.card <creature_name>', "Displays the specified creature's bestiary card.",
		"+Use flag `-g` to display the creature's gold bestiary card.",
		'+Use flag `-o` to override any binded shortcuts.'],

		['.bind <object_name>, <shortcut_1>, [shortcut_2], ...', 'Binds the object name to one or more shortcut phrases.',
		'+Use flag `-v` to view all binded shortcuts (no arguments required).',
		'+Use flag `-d` to delete shortcuts for specified objects (at least one object_name required).',
		'+Parameters are case-insensitive and must be separated by a comma.'],

		['.chop <item_name_1> <quantity_1>, [item_name_2] [quantity_2], ...', 'Adds one or more specified items to the Chopping List.',
		'+Use flag `-v` to view all items in the Chopping List (no arguments required).',
		'+Use flag `-d` to check one or more specified items off the Chopping List (quantity is optional; item will be marked as fully completed).',
		"+Use flag `-r` to reset the entire Chopping List (the word 'confirm' is required).",
		f'+Parameters are case-insensitive and there is a maximum of {MAX_CHOPPING_INPUT} parameters per entry.',
		'+Commas are optional unless two item_names are arranged consecutively.'],

		['.todo <task_description>, [priority_level]', 'Adds the given task to the Task Scheduler.',
		"+Use flag `-e` to edit a task's priority level (task_ID and new priority level required).",
		'+Use flag `-v` to view all pending tasks in the Task Scheduler (no arguments required).',
		'+Use flag `-d` to check one or more specified tasks off the Task Scheduler (at least one task_ID is required).',
		"+Use flag `-r` to reset the entire Task Scheduler (the word 'confirm' is required).",
		"+Valid task priority levels are: 'Low', 'Medium', 'High', 'Recurring'. Defaults to 'Medium' if not provided."]
	],

	'Utility': [
		['.help [page_number]', 'Displays this help menu.'],
		['.clear', 'Clears the webpage data and object information caches.'],
		['.purge', 'Purges up to 100 recent messages (in server channels), and all bot messages (in private chats).'],
		['.sleep', 'Toggles sleep mode (ignores all other user commands).']
	]
}


# dictionary of typical messages used by the bot, including warning and error messages
BOT_VOICELINES = {
	'hello': 'Hello there! Acting science manager B-B-B-BURG.L at your service!',
	'sleeping': 'Shutting down to recharge!',
	'updating': 'Available OS update detected, please stand by while I restart.',
	'debug': 'My data caches are missing!',
	'cleared': 'Data caches have been cleared.',
	'assets_updated': 'New sign images available in the Swap Shop!',
	'branch_active': 'Movement detected on VAR1 branch of the Oak Tree!',
	'purging': 'Purging message history...',
	'processing': 'Processing input...',
	'unauthorised': 'You are not authorised to use this command.',
	'empty': 'Please provide valid input parameters.',
	'need_confirmation': "This command flag requires 'confirm' as a parameter.",
	'insufficient': 'A minimum of two comma-separated parameters are required.',
	'chop_exceeded': f'A maximum of {MAX_CHOPPING_INPUT} items are allowed per entry.',
	'no_display': 'There is nothing to display.',
	'embed_close': 'Menu has been closed.',
	'list_reset': 'The specified list has been reset.',

	101: "**ERROR 101:** Unable to locate VAR1. Try typing in the object's full name.",
	102: '**ERROR 102:** Wiki page for VAR1 has an unsupported layout.',
	103: '**ERROR 103:** Google API daily limit exceeded. Type in the exact name of VAR1.',
	104: '**ERROR 104:** Unable to locate Creature Card for VAR1. Type in the exact name of the creature.',
	105: '**ERROR 105:** VAR1 is not a valid object for the Chopping List.',
	106: '**ERROR 106:** VAR1 is not present in the list.'
}


# dictionary of the available Discord statuses for the bot
# if activity (key) is meant to be a 'Streaming' activity, then corresponding value is a string URL
# otherwise corresponding value is the respective ActivityType

# available ActivityTypes: 0 is gaming (Playing), 1 is streaming (Streaming), 2 is listening (Listening to),
# 3 is watching (Watching), 4 is custom, 5 is competing (Competing in)
BOT_ACTIVITY_STATUSES = {
	'with a pet gnat': 0,
	'with a pet aphid': 0,
	'with a pet weevil': 0,
	'audio logs': 2,
	'the ladybugs coo': 2,
	'the backyard': 3,
	'the fungus spread': 3,
	'the teens': 3, 'the Watcher': 3,
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

	'Fresh': '<:ElementalType_Fresh:977409544315621467>',
	'Spicy': '<:ElementalType_Spicy:977409544206553138>',
	'Salty': '<:ElementalType_Salty:977409544495980564>',
	'Sour': '<:ElementalType_Sour:977409544344993802>',

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
OBJECT_ATTRIBUTES = {
	'aggression': 1,
	'category': 1,
	'species': 1,
	'source': (1, 'Source(s)'),

	'tier': 2,
	'gender': 2,

	'tamewith': (3, 'Tame with'),

	'damage': 4,
	'health': 4,
	'defense': 4,

	'stun': 5,
	'food': 5,
	'sturdiness': 5,

	'immune': (6, 'Immune to'),
	'speed': 6,
	'water': 6,
	'weight': 6,

	'effects': 7,

	'upgradeeffect': (8, 'Sleek Upgrade Effect'),

	'loot': 10
}
