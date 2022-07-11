import global_constants

from discord import DMChannel, Embed, Status

from secrets import *
from bot_tasks import *
from card_search import *
from bot_messaging import *
from object_search import *
from bind_functions import *
from chop_functions import *
from todo_functions import *
from global_constants import *
from storage_functions import *
from string_processing import *


# all bot methods below have to correspond to an item in BOT_COMMAND_LIST
# and must share the same name, followed by '_method'

# help menu method
async def help_method(message, user_input, flag_presence):
	embed_list = []
	category_names = ['Main', 'Utility']

	for page in range(len(category_names)):
		category = category_names[page]
		help_embed = Embed(title='**Command List**', description=f'**{category}**', color=EMBED_COLOR_CODE)

		for command in BOT_HELP_MENU[category]:

			# italicise lines that start with +
			for index in range(len(command)):
				if command[index][0] == '+':
					command[index] = f'*{command[index]}*'

			help_embed.add_field(name=command[0], value='\n'.join(command[1:]), inline=False)

		help_embed.set_footer(text=f'Page {page + 1}/{len(category_names)}')
		embed_list.append(help_embed)

	await multipage_embed_handler(message, user_input, embed_list)


# object search method
async def search_method(message, user_input, flag_presence):
	if user_input == '':
		return await burgl_message('empty', message)

	result = process_object_input(user_input, flag_presence)

	# check for errors and proceed if none detected
	if await detect_errors(message, user_input, result):
		await message.channel.send(embed=format_object_info(result))


# creature card search method
async def card_method(message, user_input, flag_presence):
	if user_input == '':
		return await burgl_message('empty', message)

	# check for existing shortcut binding in database if not overridden
	elif not flag_presence['override']:
		full_name = retrieve_full_name(user_input)

	result = get_creature_card(full_name, flag_presence['gold'])

	# check for errors and proceed if none detected
	if await detect_errors(message, user_input, result):
		embedded_card = Embed(title=f'{result[0]}', color=EMBED_COLOR_CODE)
		embedded_card.set_image(url=result[1])
		embedded_card.set_footer(text='Creature Card')

		await message.channel.send(embed=embedded_card)


# shortcut binding method
async def bind_method(message, user_input, flag_presence):
	if flag_presence['view']:  # allow non-elevated users to view bindings
		await bind_view(message, user_input)

	elif not check_user_elevation(message):
		await burgl_message('unauthorised', message)

	elif user_input == '':
		await burgl_message('empty', message)

	elif flag_presence['delete']:
		await bind_delete(message, user_input)

	else:
		await bind_default(message, user_input)


# chopping list method
async def chop_method(message, user_input, flag_presence):
	if flag_presence['view']:
		await chop_view(message, user_input)

	elif not check_user_elevation(message):
		await burgl_message('unauthorised', message)

	elif flag_presence['reset']:
		await chop_reset(message, user_input)

	elif user_input == '':
		await burgl_message('empty', message)

	elif flag_presence['delete']:
		await chop_delete(message, user_input)

	else:
		await chop_default(message, user_input)


# task scheduler method
async def todo_method(message, user_input, flag_presence):
	if flag_presence['view']:
		await todo_view(message, user_input)

	elif not check_user_elevation(message):
		await burgl_message('unauthorised', message)

	elif flag_presence['reset']:
		await todo_reset(message, user_input)

	elif user_input == '':
		await burgl_message('empty', message)

	elif flag_presence['delete']:
		await todo_delete(message, user_input)

	elif flag_presence['edit']:
		await todo_edit(message, user_input)

	else:
		await todo_default(message, user_input)


# cache clearing method
async def clear_method(message, user_input, flag_presence):
	if not check_user_elevation(message):
		await burgl_message('unauthorised', message)
	else:
		clear_cache()
		await burgl_message('cleared', message)


# message purging method
async def purge_method(message, user_input, flag_presence):
	await burgl_message('purging', message)

	# flatten message history into a list
	message_history = [old_message async for old_message in message.channel.history()]

	# if message is from a server channel
	if not isinstance(message.channel, DMChannel):
		await message.channel.delete_messages(message_history)

	else:  # if message is from a private message
		for old_message in message_history:
			if old_message.author == global_constants.BOT_INSTANCE.user:
				await old_message.delete()


# store full command list locally in this script
# can also be accessed by referencing BOT_COMMAND_LIST itself at any time, but just use a clearer name to avoid confusion 
full_command_list = BOT_COMMAND_LIST

# toggle sleep mode method
async def sleep_method(message, user_input, flag_presence):
	if DEBUG_MODE:
		# ignore command if in development mode
		return

	elif not check_user_elevation(message):
		return await burgl_message('unauthorised', message)

	sleep_command = ['sleep']

	if global_constants.BOT_COMMAND_LIST == sleep_command:  # switch off sleep mode
		global_constants.BOT_COMMAND_LIST = full_command_list

		await burgl_message('hello', message)
		rotate_status.start()

	else:
		global_constants.BOT_COMMAND_LIST = sleep_command

		await burgl_message('sleeping', message)
		await global_constants.BOT_INSTANCE.change_presence(status=Status.idle)
		rotate_status.cancel()
