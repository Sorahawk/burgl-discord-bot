from storage_functions import *

from discord import Embed
from global_variables import *

from discord import DMChannel
from asyncio import TimeoutError
from string_processing import burgl_message


# default subfunction to bind at least one shortcut to a full object name
async def bind_default(message, user_input):
	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	if len(user_input) < 2:
		return await message.channel.send(burgl_message('insufficient'))

	formatted_string = bind_shortcuts(user_input[0], user_input[1:])
	await message.channel.send(formatted_string)


# view all existing bindings
async def bind_view(bot, message, user_input):
	left_arrow = CUSTOM_EMOJIS['LeftArrow']
	cross_mark = CUSTOM_EMOJIS['CrossMark']
	right_arrow = CUSTOM_EMOJIS['RightArrow']


	# returns True if emoji reaction by user to the specific embed message is one of the specified emojis
	def multipage_emoji_check(reaction, user):
		return user != bot.user and reaction.message.id == embedded_message.id and reaction.emoji in [left_arrow, cross_mark, right_arrow]


	shortcut_list = retrieve_all_shortcuts()

	# create embeds until all shortcuts are in a page (max fields per page can be manually set, but the actual max by Discord is 25)
	embed_list = []
	number_pages = (len(shortcut_list) // MAX_SHORTCUT_FIELDS) + 1

	for page in range(number_pages):
		shortcut_embed = Embed(title='**Binded Shortcuts**', color=0x6542E1)

		start_index = page * MAX_SHORTCUT_FIELDS
		end_index = start_index + MAX_SHORTCUT_FIELDS

		for binded_pair in shortcut_list[start_index:end_index]:
			shortcuts = ', '.join(binded_pair[1])
			shortcut_embed.add_field(name=binded_pair[0], value=f'*{shortcuts}*', inline=False)

		shortcut_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(shortcut_embed)

	current_page = 0

	embedded_message = await message.channel.send(embed=embed_list[current_page])
	await embedded_message.add_reaction(left_arrow)
	await embedded_message.add_reaction(cross_mark)
	await embedded_message.add_reaction(right_arrow)

	while True:
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=60, check=multipage_emoji_check)

			if reaction.emoji == cross_mark:
				if isinstance(message.channel, DMChannel):  # check if channel is a private chat
					return await embedded_message.delete()

				else:
					await embedded_message.clear_reactions()
					return await embedded_message.edit(content=burgl_message('embed_close'), embed=None)

			elif reaction.emoji == left_arrow:
				if current_page == 0:
					# wrap-around to the end
					current_page = number_pages - 1
				else:
					current_page -= 1

			elif reaction.emoji == right_arrow:
				if current_page == number_pages - 1:
					# wrap-around to the start
					current_page = 0
				else:
					current_page += 1

			await embedded_message.edit(embed=embed_list[current_page])

			if not isinstance(message.channel, DMChannel):
				await embedded_message.remove_reaction(reaction, user)

		except TimeoutError:
			try:
				# after specified timeout period, remove 'buttons' from the message
				# leaves the info on screen, but also informs the user that pages can no longer be navigated
				return await embedded_message.clear_reactions()

			except:  # other errors, like discord.errors.NotFound: Unknown Message (if message is deleted)
				return


# delete all shortcuts for one or more specified object names
async def bind_delete(message, user_input):
	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	formatted_string = delete_shortcuts(user_input)

	if formatted_string:
		await message.channel.send(formatted_string)
	else:
		await message.channel.send(burgl_message('invalid_bind'))
