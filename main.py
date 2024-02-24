import discord

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = ['!'], #if this errors, remove the list.
            intents = discord.Intents.all()
        )
    
    async def setup_hook(self):

      print('--------------------------------')
      print('Verison:', discord.__version__)
      print('Bot is now online!')
      print("Name: ", (self.user.name))
      print("ID:", (self.user.id))
      print("Time:", (datetime.now().astimezone()))
      print('--------------------------------')

      await self.load_extension('tictactoe')
      
  

bot.run(TOKEN) #<- your bot token
