
# symbols to ignore from user input as most of these will cause a 'Bad Title' page on the wiki
# used by helper_functions.get_appended_url()
ILLEGAL_URL_SYMBOLS = '[\][}{><|%+]+'

# sets the minimum threshold of similarity between search query and predicted result
# used by object_search_functions.locate_object_url()
SIMILARITY_THRESHOLD = 0.35

# smoothie bases and their base ingredients
# used by helper_functions.detect_smoothie_type() and object_search_functions.get_recipe_table() 
SMOOTHIE_BASES = {'basic': 'Grub Goop', 'beefy': 'Muscle Sprout', 'sticky': 'Gum Nugget'}
