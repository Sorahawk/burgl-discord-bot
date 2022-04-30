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
| Object Search | Retrieves object information |
| Status Effect Search | Retrieves status effect information |
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

- [X] Object Search
    - [X] Google APIs (Programmable Search Engine and Custom Search JSON) integration as an option to locate page URLs
    - [X] Creature Search
    - [X] Item Search
- [X] Discord Bot Functionality
- [X] Overhaul current extraction algorithms (Creature and Item Search) with modular style of detecting data to make them inherently compatible with more pages
    - [X] Infobox extraction
    - [X] Recipe extraction
        - [X] Smoothie recipe special case
    - [X] Equipment repair cost extraction
    - [X] Object tier extraction
    - [X] Process special smoothie type from input
    - [X] Single armor piece sleek upgrade extraction
    - [ ] Armor set info extraction
- [ ] Status Effect Search
- [ ] Help Display
- [ ] Hosting on Heroku (or EC2, if Heroku can't upload multiple scripts)
- [ ] Manually record BURG.L's in-game voicelines
- [ ] Set up proper environment files for API keys which can be hidden from GitHub, so repo could possibly be made public 
- [ ] Database Implementation
- [ ] Command for user to bind search queries directly to URL of desired object, or maybe just the postfix
- [ ] Cache all search queries to the resulting URL within Heroku
- [ ] Chopping List
    - [ ] Ability to recognise multiple items from a user string
    - [ ] Print back to user the items that were successfully added
    - [ ] User is able to remove any errors
    - [ ] Sum and multiply item costs using collections.Counter
    - [ ] Ability to continuously consolidate materials
- [ ] Task Scheduler
    - [ ] Track user-inputted tasks, with user-set priority
    - [ ] Generate list of tasks in order of priority, task ID assigned from highest to lowest priority
    - [ ] Allow user to complete tasks
    - [ ] Generate harvesting tasks with priority based on chopping list
- [ ] Telegram Bot Functionality
    - [ ] Perhaps just the function to view the current tasks which can assist planning in the Telegram group


<p align="right">(<a href="#top">back to top</a>)</p>

---

Copyright © 2022, [Sorahawk](https://github.com/Sorahawk)
