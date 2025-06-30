# RandomFactsBot
I have created the telegram bot, which sends you a random fact every day at 8 pm by Moscow time.

When you click on command "start", your id and username go to the database table, so that the bot knows who to send the facts to at the appointed time. As I was saying, the bot sends you a random fact at a certain time. If user blocks the bot, I will get message from bot, that message wasn't delivered and user id, who blocked the bot.

You also can use bar with special buttons. If you click on the first button, you can get random fact anytime. By clicking the second button you can suggest your fact and it goes to the database table with username so that no one sends offensive messages.

You also have the "help" command, which brings up a message with a recommendation and my contact.

As a database, I used SQLite. Now there are 154 facts stored in the database.

in the future, I plan to connect the bot to a free online server so that the bot works around the clock and expands the database with facts.

That was my first telegram bot, so I have a lot of things left to learn. Have fun using it😊
