from discord import Embed
from asyncio import TimeoutError
from string_processing import burgl_message
from storage_functions import bind_query_name, retrieve_all_shortcuts


# default subfunction to bind at least one shortcut to a full object name
async def bind_default(message, user_input):
	user_input = user_input.lower().strip(',').split(',')  # remove any edge commas, then split by comma

	if len(user_input) < 2:
		return await message.channel.send(burgl_message('insufficient'))

	formatted_string = bind_query_name(user_input[0], user_input[1:])
	await message.channel.send(formatted_string)


# view all existing bindings
async def bind_view(bot, message, user_input):
	left_arrow = '◀️'
	right_arrow = '▶️'

	shortcut_list = retrieve_all_shortcuts()

	# each embed has max of 25 fields, so create embeds until all shortcuts are in
	embed_list = []
	number_pages = len(shortcut_list) // 25 + 1

	for page in range(number_pages):
		shortcut_embed = Embed(title='Binded Shortcuts', colour=0x6542E1)

		start_index = 0 + page * 25
		end_index = start_index + 25

		for binded_pair in shortcut_list[start_index:end_index]:
			shortcuts = ', '.join(binded_pair[1])
			shortcut_embed.add_field(name=binded_pair[0], value=shortcuts, inline=False)

		shortcut_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(shortcut_embed)

	current_page = 0
	embed_message = await message.channel.send(embed=embed_list[current_page])

	await embed_message.add_reaction(left_arrow)
	await embed_message.add_reaction(right_arrow)


	# returns True if emoji reaction by user to the specific embed message is one of the specified emojis
	def multipage_emoji_check(reaction, user):
		return user != bot.user and reaction.message.id == embed_message.id and reaction.emoji in [left_arrow, right_arrow]


	while True:
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=60, check=multipage_emoji_check)

			if reaction.emoji == right_arrow and current_page != number_pages - 1:
				current_page += 1

			elif reaction.emoji == left_arrow and current_page != 0:
				current_page -= 1

			await embed_message.edit(embed=embed_list[current_page])
			await embed_message.remove_reaction(reaction, user)

		except TimeoutError:
			try:
				# after specified timeout period, remove arrow 'buttons' from the message
				# leaves the info on screen, but also informs the user that pages can no longer be navigated
				await embed_message.clear_reactions()
				break

			except:  # other errors, like discord.errors.NotFound: Unknown Message (if message is deleted)
				break
