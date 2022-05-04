
# dictionary to store all the possible Discord statuses for the bot
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


# dictionary to store custom server emojis
CUSTOM_EMOJIS = {'BURG.L': '<:BURGL_Icon:970544869124755467>', 'Fresh': '<:ElementalType_Fresh:970550878966796308>',\
				'Salty': '<:ElementalType_Salty:970550879226847302>', 'Spicy': '<:ElementalType_Spicy:970551950405947453>',\
				'Busting': '<:DamageType_Busting:970552005250646036>', 'Chopping': '<:DamageType_Chopping:970552005883998269>',\
				'Digging': '<:DamageType_Digging:970552065577328650>', 'Explosive': '<:DamageType_Explosive:970552089493262346>',\
				'Slashing': '<:DamageType_Slashing:970552106496978964>', 'Stabbing': '<:DamageType_Stabbing:970552122548559872>'}


# symbols to ignore from user input as most of these will cause a 'Bad Title' page on the wiki
ILLEGAL_URL_SYMBOLS = '[\][}{><|%+]+'


# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 970882023055036426


# sets the minimum threshold of similarity between search query and predicted result
SIMILARITY_THRESHOLD = 0.35


# smoothie bases and their base ingredients
SMOOTHIE_BASES = {'basic': 'Grub Goop', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}
