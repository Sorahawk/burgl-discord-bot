<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Sorahawk/BURG.L_Discord_Bot">
    <img src="images/logo.jpg" alt="Logo" width="225" height="200">
  </a>
  <h3 align="center">BURG.L Discord Bot</h3>
  <p align="center">
    Discord resource management bot that augments the Grounded gaming experience
  </p>
</div>



# About The Project

The BURG.L Discord Bot is a resource manager that aids [Grounded](https://grounded.obsidian.net/) players by tracking requirements and allocating tasks. BURG.L pulls data from the [Grounded Wiki](https://grounded.fandom.com/wiki/Grounded_Wiki) to get information for items, such as crafting costs. Despite the recent introduction of slash commands by Discord, prefix commands are still used in this project as Discord's in-game overlay does not work with slash commands.


## Planned Features

| Feature | Description |
| ------- | ----------- |
| Object Search | Retrieves object information (e.g. Creatures, Items, Resources, Status Effects, Mutations) |
| Chopping List | Consolidates total number of resources required for crafting and building. |
| Task Scheduler | Keeps track of user-inputted tasks, as well as generating harvesting tasks based on the Chopping List |


## Built With

* [Python](https://www.python.org/)
* [Discord.py](https://discordpy.readthedocs.io/)
* [Programmable Search Engine by Google](https://programmablesearchengine.google.com/)
* [Custom Search JSON API by Google](https://developers.google.com/custom-search/v1/introduction)
* [Amazon EC2](https://aws.amazon.com/ec2/) or [Heroku](https://www.heroku.com/)
* [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) ~~or [Amazon S3](https://aws.amazon.com/s3/)~~



# Usage

## Bot Commands

* `.help` - Display this list
* `.search <object_name>` - Display details of the object, including its picture and description.
  * If the object is a creature, its aggression trait and loot tables are also shown.
  * If the object is an item, its category and crafting recipe (if any) are also shown.


## Error Codes

| Code | Description |
| ---- | ----------- |
| 101 | Wiki page for the object cannot be located. |
| 102 | Wiki page for the object has an unsupported layout. |
| 103 | Daily limit of 100 queries for Google Custom Search JSON API has been exceeded. |



# Roadmap

- [X] Object search
    - [X] Google APIs (Programmable Search Engine and Custom Search JSON) integration as an option to locate page URLs
    - [X] Creature search
    - [X] Item search
- [X] Discord bot functionality
- [X] Overhaul object (creature and item) Search with new modular style of extracting data to be inherently compatible with more pages
    - [X] Infobox extraction
    - [X] Recipe extraction
    - [X] Repair cost extraction
    - [X] Specify smoothie type from input, with corresponding base added to recipe
- [X] Modifiers (Status effects and Mutations) extraction merged into `.search`
- [ ] Full armor set info extraction
- [ ] `.help` command
- [ ] Hosting on Heroku (or EC2, if Heroku can't upload multiple scripts)
- [ ] Cache implementation (Ephemeral storage)
    - [ ] Ability to cache dictionary of object information upon successful retrieval
    - [ ] Ability to retrieve dictionary of object information from cache
- [ ] Database implementation (DynamoDB)
    - [ ] Command to manually link search terms to desired URLs (requires elevation)
- [ ] Chopping List
    - [ ] Ability to recognise multiple items from a user string, along with their respective quantities
    - [ ] Display the items that were successfully added
    - [ ] Able to manually remove any errors
    - [ ] Sum and multiply item costs using collections.Counter
    - [ ] Ability to continuously update a persistent chopping list
- [ ] Task Scheduler
    - [ ] Track user-inputted tasks, with user-set priority
    - [ ] Generate list of tasks in order of priority, task ID assigned from highest to lowest priority
    - [ ] Allow user to complete tasks
    - [ ] Generate harvesting tasks with priority based on chopping list
- [ ] Tweak Discord BURG.L bot's lines to sound more like in-game BURG.L
    - [ ] Manually record BURG.L's in-game voicelines
- [ ] Telegram Bot Functionality
    - [ ] View current tasks in Task Scheduler


<p align="right">(<a href="#top">back to top</a>)</p>

---

Copyright © 2022, [Sorahawk](https://github.com/Sorahawk)
