import discord
from discord import app_commands
import random
from datetime import datetime, timedelta

bot = commands.Bot(case_insensitive = True, command_prefix = "?", intents=discord.Intents.all(), status = discord.Status.idle)#<- choose your own prefix

@bot.event
async def on_ready():
  # READ COMMENT!!!
  try:
    synced = await bot.tree.sync()
    synced_list = []
    
    for item in synced:
      synced_list.append(item.name)

    print(f'Synced {len(synced)}/{len(bot.commands)} commands\n{synced_list}')
    
  except Exception as e:
    print(e)

  await bot.load_extension('tictactoe') #load the extension by file name
  
  print('--------------------------------')
  print('Version:', discord.__version__)
  print('Truth Bot is online!')
  print("Name: ", (bot.user.name))
  print("ID:", (bot.user.id))
  print(f'{datetime.now().astimezone()}')
  print('--------------------------------')

  
  
  #######################################################
  # TTT_CHECK
  """ 
  "ttt_check" is called after each button is clicked to checks if a user has sucessfully made 3 matching signs in a row. This returnsa bool based on the results.
  "possible_wins" is exactly as the name suggest. It is a list that has the winning possible moves. This is looped through and campared with the "board" which the dict "self.ttt_moves"
  "won" will remain "False" until changed to "True" if 3 of the same signs are found in row
  """
  #######################################################
  

bot.run(TOKEN) #<- your bot token
