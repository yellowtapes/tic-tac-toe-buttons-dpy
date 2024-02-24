import discord
import os, io, re
import asyncio, aiohttp

from discord import ui, app_commands
from datetime import datetime, timedelta
from discord.ext import commands

import random
from datetime import datetime

ttt_status = {}
ttt_queue = {}

async def ttt_check(self, interaction, board, sign):
    possible_wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    won = False

    for a, b, c in possible_wins:
    
      if board[a] == sign and board[b] == sign and board[c] == sign: #checks the board (buttons) and their signs (emojis) to see if they match
        won = True                                                   # if so, someone has won
  
    if won == True:
     
      embed = discord.Embed(
       title = f'Tic Tac Toe\n{self.player1.display_name} vs {self.player2.display_name}',
       description = f"{self.sign} {self.turn.mention} won! 🎉\n\n*Wager*:\n> {self.wager}",
       color = discord.Color(0x2F3136)
      )
  
      self.top_left.disabled = True
      self.top_centre.disabled = True
      self.top_right.disabled = True
      self.mid_left.disabled = True
      self.mid_centre.disabled = True
      self.mid_right.disabled = True
      self.bottom_left.disabled = True
      self.bottom_centre.disabled = True
      self.bottom_right.disabled = True
      self.redo.disabled = False
      self.surrender.disabled = True
      self.timeout = None
     
      await interaction.message.edit(content = self.turn.mention, embed = embed, view = self)
      del(ttt_status[f'{interaction.guild.id}|{self.player1.id}'])
      del(ttt_status[f'{interaction.guild.id}|{self.player2.id}'])
      return #if someone one, we send the winning embed and remove both players from the dict so they can create another game
    
     
    if self.count != 9: #if the amount of plays does not equal 9, then the game has not been concluded just yet
    
      if self.sign == self.X:
        self.sign = self.O
    
      else:
        self.sign = self.X
      
      if self.turn == self.player1:
        self.turn = self.player2
      
      else:
        self.turn = self.player1
    
      embed = discord.Embed(
        title = f'Tic Tac Toe\n{self.player1.display_name} vs {self.player2.display_name}',
        description = f"It's {self.turn.mention}'s turn! You are {self.sign}\n*Turn ends {discord.utils.format_dt(datetime.now().astimezone() + timedelta(seconds = 60.0), style = 'R')}*\n\n*Wager*:\n> {self.wager}",
        color = discord.Color(0x2F3136)
      )
      
      await interaction.message.edit(content = self.turn.mention, embed = embed, view = self)
       
    else: # if it is as no one has one, it's an obv draw, cause there is no more possible plays pass 9.
       
       embed = discord.Embed(
         title = f'Tic Tac Toe\n{self.player1.display_name} vs {self.player2.display_name}',
         description = f"Well, no one won, It's a draw! 👀\n\n*Wager*:\n> ~~{self.wager}~~",
         color = discord.Color(0x2F3136)
        )
      
       self.top_left.disabled = True
       self.top_centre.disabled = True
       self.top_right.disabled = True
       self.mid_left.disabled = True
       self.mid_centre.disabled = True
       self.mid_right.disabled = True
       self.bottom_left.disabled = True
       self.bottom_centre.disabled = True
       self.bottom_right.disabled = True
       self.redo.disabled = False
       self.surrender.disabled = True
       self.timeout = None  
      
       await interaction.message.edit(content = '', embed = embed, view = self)




#######################################################
  # TTT_REQUEST
""" 
This is the view that is sent when a user issues the command and request a user to play with them.
"""
####################################################### 

class ttt_request(discord.ui.View):
    def __init__(self, requesting, requested, interaction):
        super().__init__(timeout = 120.0)
        self.requesting = requesting              #user who is requesting to play.
        self.requested = requested                #the user who is being requested to play with the "requesting".    
        self.interaction = interaction            #this is for the "on_timeout" event. [DO NOT TOUCH UNLESS YOU KNOW WHAT YOUR DOING!!!]
        self.accepted = False                     #used to check if the button "accept" was clicked.
        self.declined = False                     #used to check if the button "decline" was clicked.

    
    async def on_timeout(self) -> None:
      self.clear_items()

      embed = discord.Embed(
       title = 'Challenge Auto Declined',
       description = '> User did not respond to your challenge request.',
       color = discord.Color.red()
      )
     
      await self.interaction.edit_original_response(content = self.interaction.user.mention, embed = embed, view = self)
      del(ttt_status[f'{self.interaction.guild.id}|{self.requesting.id}'])

    
    @discord.ui.button(label= 'Accept', style = discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()

      if interaction.user == self.requested:
         
         self.clear_items()                                # remove all buttons from the message.
         self.accepted = True                              # initialize that "accept" was clicked.
         await interaction.message.edit(view = self)       # update the view of the changes.
         
         return self.stop()                                # stops the view, this triggers the "request.wait()" function.
      
         
    
    @discord.ui.button(label= 'Decline', style = discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if interaction.user == self.requested:
           
          self.clear_items()
          self.declined = True
          await interaction.message.edit(view = self)
        
        elif interaction.user == self.requesting:
          
          self.clear_items()
          embed = discord.Embed(
            title = 'Challenged Cancelled',
            description = f'> {interaction.user.mention} cancelled their challenge request.',
            color = discord.Color.red()
          )

          await interaction.message.edit(embed = embed, view = self)
        
        return self.stop()
  

class tic_tac_toe(discord.ui.View):
    def __init__(self, player1, player2, turn, sign, wager, interaction):
        super().__init__(timeout = 60.0)
        self.player1 = player1
        self.player2 = player2
        self.turn = turn
        self.sign = sign
        self.X = '❌'
        self.O = '⭕'
        self.wager = wager
        self.interaction = interaction
        self.topleft = False    # ⬇️THESE ARE USED TO DETERMINE WHICH BUTTON WAS CLICKED ALREADY⬇️
        self.topcentre = False
        self.topright = False
        self.midleft = False
        self.midcentre = False
        self.midright = False
        self.bottomleft = False
        self.bottomcentre = False
        self.bottomright = False
        self.redo_clicked = False # ⬆️THESE ARE USED TO DETERMINE WHICH BUTTON WAS CLICKED ALREADY⬆️
        self.count = 0            # this is used to determine when all buttons have been clicked. If someone didn't win or lose before this reaches 9, it's an obvious draw.
        
        self.ttt_moves = {0: "None", 1: "None", 2: "None",   #this is the board set up. This is what the code see's and uses to determine what changes we're made to the game
                        3: "None", 4: "None", 5: "None",     # this is also passed into "ttt_check()" as "board", visual demonstration, " ttt_check(board = self.ttt_moves, sign = ...) "
                        6: "None", 7: "None", 8: "None"
                        }

    async def on_timeout(self) -> None:
       
       if self.sign == self.X:             #changed the sign to declare that the next person is the winner
         self.sign = self.O
       
       else:
         self.sign = self.X
       
       if self.turn == self.player1:      #changes the player
         self.turn = self.player2
         loser = self.player1             #based on who the winner is we can of course determine the loser
       
       else:
         self.turn = self.player1
         loser = self.player2

       embed = discord.Embed(
          title = f'Tic Tac Toe\n{self.player1.display_name} vs {self.player2.display_name}',
          description = f"{loser.mention} failed to play in time.\n{self.sign} {self.turn.mention} won! 🎉\n\n*Wager*:\n> {self.wager}",
          color = discord.Color(0x2F3136)
        )
         
       self.top_left.disabled = True
       self.top_centre.disabled = True
       self.top_right.disabled = True
       self.mid_left.disabled = True
       self.mid_centre.disabled = True
       self.mid_right.disabled = True
       self.bottom_left.disabled = True
       self.bottom_centre.disabled = True
       self.bottom_right.disabled = True
       self.redo.disabled = True
       self.surrender.disabled = True
     
       await self.interaction.edit_original_response(content = '', embed = embed, view = self)


    @discord.ui.button(label= '', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>',  row = 0)
    async def top_left(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer() #we need this since we are not responding to the interaction 


      if self.topleft == True:                        #this checks if the button was clicked by a player before. Nothing will happen if it was.
        return
      
      else:
         self.topleft = True
      
      if self.turn == interaction.user:               #makes sure the person clicking the button is the person whos turn it is
           
        button.emoji = self.sign                      #sets the button emoji to the current "sign"
        self.count += 1                               #now that a move was made, we count that as + 1
        self.ttt_moves[0] = self.sign               #this is the important part. The dict is updated with the "position" which is where was clicked (from 0 - 8) along with the which "sign" ('⭕' or '❌') was added into the dict. 
        self.topleft = True

        await ttt_check(self, interaction, self.ttt_moves, self.sign)
      
      elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:    #this checks if the user who clicked the button was a player, and if they are not the one who's in turn, they are ask to wait.
        await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
      
      else:   #if the user is not a player of the gameall together, they are ignored. And their button click is not counted nor registered or handled.
        return
    
    
    
    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 0)
    async def top_centre(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()

      if self.topcentre == True:
        return
      
      if self.turn == interaction.user:

        button.emoji = self.sign
        self.count += 1
        self.ttt_moves[1] = self.sign
        self.topcentre = True

        await ttt_check(self, interaction, self.ttt_moves, self.sign)
      
      elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
        await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
      
      else:
        return
          

    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 0)
    async def top_right(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()

      if self.topright == True:
        return
      
      if self.turn == interaction.user:

           button.emoji = self.sign
           self.count += 1
           self.ttt_moves[2] = self.sign
           self.topright = True

           await ttt_check(self, interaction, self.ttt_moves, self.sign)
      
      elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
        await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
      
      else:
        return
      

    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 1)
    async def mid_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.midleft == True:
          return
        
        if self.turn == interaction.user:
             
            button.emoji = self.sign
            self.count += 1
            self.ttt_moves[3] = self.sign
            self.midleft = True
  
            await ttt_check(self, interaction, self.ttt_moves, self.sign)
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
      
    
    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 1)
    async def mid_centre(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.midcentre == True:
          return
        
        if self.turn == interaction.user:
             
             button.emoji = self.sign
             self.count += 1
             self.ttt_moves[4] = self.sign
             self.midcentre = True
  
             await ttt_check(self, interaction, self.ttt_moves, self.sign)
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
      
    
    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 1)
    async def mid_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.midright == True:
          return
        
        if self.turn == interaction.user:
  
             button.emoji = self.sign
             self.count += 1
             self.ttt_moves[5] = self.sign
             self.midright = True
  
             await ttt_check(self, interaction, self.ttt_moves, self.sign)
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
    

    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 2)
    async def bottom_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.bottomleft == True:
          return
        
        if self.turn == interaction.user:
  
           if self.bottomleft == False:
             button.emoji = self.sign
             self.count += 1
             self.ttt_moves[6] = self.sign
             self.bottomleft = True
  
             await ttt_check(self, interaction, self.ttt_moves, self.sign)
      
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
      
    

    @discord.ui.button(label='', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>', row = 2)
    async def bottom_centre(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.bottomcentre == True:
          return
        
        if self.turn == interaction.user:
  
             button.emoji = self.sign
             self.count += 1
             self.ttt_moves[7] = self.sign
             self.bottomcentre = True
  
             await ttt_check(self, interaction, self.ttt_moves, self.sign)
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
      
    
    @discord.ui.button(label= '', style = discord.ButtonStyle.grey, emoji = '<:space_t:1097706688871673886>',  row = 2)
    async def bottom_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
  
        if self.bottomright == True:
          return
        
        if self.turn == interaction.user:
  
             button.emoji = self.sign
             self.count += 1
             self.ttt_moves[8] = self.sign
             self.bottomright = True
  
             await ttt_check(self, interaction, self.ttt_moves, self.sign)
      
        
        elif interaction.user == self.player1 and self.player1 != self.turn or interaction.user == self.player2 and self.player2 != self.turn:
          await interaction.followup.send("It is currently not your turn. Please wait.", ephemeral = True)
        
        else:
          return
      
    
    
    @discord.ui.button(label= '', style = discord.ButtonStyle.grey, emoji = '<:redo:1098026843006841012>',  row = 1, disabled = True)
    async def redo(self, interaction: discord.Interaction, button: discord.ui.Button):
       
       if interaction.user.id not in [self.player1.id, self.player2.id]: #checks if the persons clicking the button are on of the previous players.
          return
       
      #  elif self.top_left.disabled == False:         #basically check any button and you'd be able to determine if the game is still in process.
      #    return await interaction.response.send_message("You can't request a rematch until you finished your current game", ephemeral = True)
       
       elif self.redo_clicked == True: #checks if the button has already been clicked and responded to. Once it is, the view is expected to have ended.
          return
       
       else:
         self.redo_clicked = True  #the button wasnt clicked before, so let's go ahead and initialize that it now was.

       if interaction.user == self.player1: #here we determine which player click the button
         user = self.player2
       
       else:
          user = self.player1
       
       embed = discord.Embed(
         title = f'Tic Tac Toe',
         description = f"{interaction.user.mention} is requesting a rematch to play a game of tic tac toe.\n\n*Wager*:\n> {self.wager}\n\n*auto-declines {discord.utils.format_dt(datetime.now().astimezone() + timedelta(seconds = 120.0), style = 'R')}*",
         color = discord.Color(0x2F3136)
        )
   
       request = ttt_request(interaction.user, user, interaction)
       await interaction.response.send_message(content = user.mention, embed = embed, view = request) #then we resend a new request, and everthing is repeated.
       await request.wait()
    
       if request.accepted == True:
    
          sign = random.choice(['❌', '⭕'])
          player1 = interaction.user
          player2 = user
          turn = random.choice([player1, player2])
       
          view = tic_tac_toe(player1, player2, turn, sign, self.wager, interaction)
       
       
          embed = discord.Embed(
            title = f'Tic Tac Toe\n{player1.display_name} vs {player2.display_name}',
            description = f"It's {turn.mention}'s turn! You are {sign}\n*Turn ends {discord.utils.format_dt(datetime.now().astimezone() + timedelta(seconds = 60.0), style = 'R')}*\n\n*Wager*:\n> {self.wager}",
            color = discord.Color(0x2F3136)
           )
            
          await interaction.edit_original_response(content = turn.mention, embed = embed, view = view)
       
       elif request.declined == True:
         
         embed = discord.Embed(
           title = 'Challenge Declined',
           color = discord.Color.red()
          )
         
         await interaction.edit_original_response(content = interaction.user.mention, embed = embed, view = None)
       
       return self.stop()
    

    # @discord.ui.button(label= '', style = discord.ButtonStyle.grey, emoji = '<:challenge:1210655565966082088>',  row = 1)
    # async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        
       


    @discord.ui.button(label= '', style = discord.ButtonStyle.red, emoji = '🏳️',  row = 2)
    async def surrender(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()  
      
      if interaction.user.id not in [self.player1.id, self.player2.id]:
        return

      if self.turn == interaction.user:

        if self.sign == self.X:
          self.sign = self.O
        
        else:
          self.sign = self.X

        if self.turn == self.player1:
          self.turn = self.player2
        
        else:
          self.turn = self.player1
      
      else:

        if interaction.user == self.player1:
          self.turn = self.player2
        
        else:
          self.turn = self.player1
      
      embed = discord.Embed(
        title = f'Tic Tac Toe\n{self.player1.display_name} vs {self.player2.display_name}',
        description = f"{interaction.user.mention} surrendered.\n{self.sign} {self.turn.mention} won! 🎉\n\n*Wager*:\n> {self.wager}",
        color = discord.Color(0x2F3136)
      )
         
      self.top_left.disabled = True
      self.top_centre.disabled = True
      self.top_right.disabled = True
      self.mid_left.disabled = True
      self.mid_centre.disabled = True
      self.mid_right.disabled = True
      self.bottom_left.disabled = True
      self.bottom_centre.disabled = True
      self.bottom_right.disabled = True
      self.redo.disabled = False
      self.surrender.disabled = True
      self.timeout = None 

      await interaction.message.edit(content = self.turn.mention, embed = embed, view = self)



class TTT(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      
      
    """ORIGINAL SLASH COMMAND"""

    @app_commands.command(name = 'tictactoe', description = 'Play a classic fun game of tic tac toe')
    @app_commands.describe(user = 'Pick a user to play with.', wager = 'Choose what to bet on. eg. "Winner gets x"')
    async def tictactoe(self, interaction: discord.Interaction, user: discord.Member, wager: str = '`None`'):
       
        status = ttt_status.get(f'{interaction.guild.id}|{interaction.user.id}', None)
        
        if status is not None and type(status) is str:
          
          embed = discord.Embed(
             title = 'Pending Request',
             description = f'> You currently have a pending request to {status}.',
             color = discord.Color.red()
          )

          return await interaction.response.send_message(embed = embed, ephemeral = True)

        elif status is not None:

          try:
            channel = self.bot.get_channel(status[0])
            message = channel.fetch_message(status[1])

            embed = discord.Embed(
              title = 'Active Game.',
                url = message.jump_url,
              description = '> You have already challenged {user.mention}.',
              color = discord.Color.red()
            )
            
            return await interaction.response.send_message(embed = embed, ephemeral = True)
          
          except:
             del(ttt_status[f'{interaction.guild.id}|{interaction.user.id}'])
        
        
        if user == interaction.user:
          return await interaction.response.send_message("Trynna play with yourself I see 👀", ephemeral =  True) #stops user from playing agaisnt themselves.
        
        elif user.bot == True:
          return await interaction.response.send_message(f"{user.display_name} thought about it...and declined 🙃", ephemeral = True) #stops players from playing against bots.
        
        elif len(wager) > 50:
          return await interaction.resoponse.send_message('Your wager is too long. Shorten it a little under 50 characters.', ephemeral = True) #limits the lenght of wager, so they dont write a whole paragraph.
        
        embed = discord.Embed(
          title = f'Tic Tac Toe',
          description = f"{interaction.user.mention} is challenging you to a game of tic tac toe.\n\n*Wager*:\n> {wager}\n\n*auto-declines {discord.utils.format_dt(datetime.now().astimezone() + timedelta(seconds = 120.0), style = 'R')}*",
          color = discord.Color(0x2F3136)
         )
        
        request = ttt_request(interaction.user, user, interaction)
        await interaction.response.send_message(content = user.mention, embed = embed, view = request) #this is a request to the opponent to come play with the user
        ttt_status[f'{interaction.guild.id}|{interaction.user.id}'] = user.mention
        await request.wait()     #wait on the "ttt_request" view to timeout, so that you can manage which button was clicked and what to do.
     
        if request.accepted == True:
    
          sign = random.choice(['❌', '⭕'])
          player1 = interaction.user
          player2 = user
          turn = random.choice([player1, player2])
      
          view = tic_tac_toe(player1, player2, turn, sign, wager, interaction)
      
      
          embed = discord.Embed(
            title = f'Tic Tac Toe\n{player1.display_name} vs {player2.display_name}',
            description = f"It's {turn.mention}'s turn! You are {sign}\n*Turn ends {discord.utils.format_dt(datetime.now().astimezone() + timedelta(seconds = 60.0), style = 'R')}*\n\n*Wager*:\n> {wager}",
            color = discord.Color(0x2F3136)
           )
            
          await interaction.edit_original_response(content = turn.mention, embed = embed, view = view)
          ttt_status[f'{interaction.guild.id}|{interaction.user.id}'] = (interaction.channel.id, interaction.message.id)
          ttt_status[f'{interaction.guild.id}|{request.requested.id}'] = (interaction.channel.id, interaction.message.id)
        
        elif request.declined == True:
          
          embed = discord.Embed(
            title = 'Challenge Declined',
            color = discord.Color.red()
           )
          
          await interaction.edit_original_response(content = interaction.user.mention, embed = embed, view = None)
          del(ttt_status[f'{interaction.guild.id}|{interaction.user.id}'])


async def setup(bot):
  await bot.add_cog(TTT(bot = bot))
