import discord
from discord.ext import commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.utils import get
import bot_messages,functions
from functions import channel_list
from functions import *
intents = discord.Intents.default()
intents = discord.Intents(messages=True,guilds=True,reactions=True,members=True,presences=True) #getting discord elements

Bot = commands.Bot(command_prefix = "!",intents=intents, help_command=None) #using "!" for bot command.

@Bot.event
async def on_ready():
  print("let's go") # see this while bot is running


@Bot.command() #help command
@has_permissions(administrator=True)
async def help(ctx):
  await ctx.channel.send(bot_messages.bot_help)

  
@Bot.command()
@has_permissions(administrator=True) # you can select which user can use this command. i selected admin.
async def command_channel(ctx,arg1=None): #command channel to use bot command.

  if len(functions.command_channel_list)>=1:
    await ctx.channel.send(bot_messages.command_channel_set)
    return

  if arg1==None:
    await ctx.channel.send(bot_messages.parametres_error)
    return

  functions.command_channel_set(arg1)
  await ctx.channel.send(f"Has been set !{ctx.author.mention}")



@Bot.command()
@has_permissions(administrator=True)
async def add_channel(ctx,arg1=None,arg2=None,arg3=None,arg4=None,encoding="utf8"): #4 parametres for bot working
  if len(functions.command_channel_list)==0:
    await ctx.channel.send(bot_messages.set_command)
    return
  if ctx.channel.id !=int(functions.command_channel_list[0]): #checking if channel is command channel
    return await ctx.channel.send(bot_messages.command_channel_error)
  if arg1==None or arg2==None or arg3==None or arg4==None: #checking parametres is entered or not entered
    return await ctx.channel.send(bot_messages.parametres_error)
  if functions.mention_check(arg1)==False or functions.mention_check(arg2)==False: #checking channels are mentioned
    return await ctx.channel.send(bot_messages.mention_error)
  if not arg3.isdigit():
    return await ctx.channel.send(bot_messages.ammount_error) #checking for third parametres is int or not
  if not arg4.encode("utf-8"):
    return await ctx.channel.send(bot_messages.emoji_error) #checking for fourth parametres is emoji or not
  else: #adding to a list the channels
    functions.add_channel(arg1,arg2,arg3,arg4)
    await ctx.channel.send(bot_messages.channels_add)



@Bot.command()
@has_permissions(administrator=True)
async def show_channel(ctx,arg1=None): #show channel command
  if len(functions.command_channel_list)==0:
    await ctx.channel.send(bot_messages.set_command)
    return
  #if arg1 is empty, it's gonna show all channel. but if you put in something, it's gonna show that index
  if ctx.channel.id !=int(functions.command_channel_list[0]): #checking if channel is command channel
    return await ctx.channel.send(bot_messages.command_channel_error)
  count=1
  if arg1!=None and int(arg1)<=len(channel_list) and arg1.isdigit()==True: #showing channel for arg1 index
    arg1=int(arg1)
    await ctx.channel.send(
      f"**{arg1}.** **from: {Bot.get_channel(int(channel_list[arg1-1][0])).mention}**,**to: {Bot.get_channel(int(channel_list[arg1-1][1])).mention}**, **count: {channel_list[arg1-1][2]}**, **emoji: {channel_list[arg1-1][3]}**\n")
    return
  if len(channel_list)==0: #checking list is empty or not
    await ctx.channel.send(bot_messages.empty_channels)
    return

  for i in channel_list: #then shows channels that you added
    await ctx.channel.send(
      f"**{count}.** **from: {Bot.get_channel(int(i[0])).mention}**,**to: {Bot.get_channel(int(i[1])).mention}**, **count: {i[2]}**, **emoji: {i[3]}**\n")
    count+=1



@Bot.command()
@has_permissions(administrator=True)
async def delete_channel(ctx,arg1): #delete channel command
  if len(functions.command_channel_list)==0:
    await ctx.channel.send(bot_messages.set_command)
    return
  if ctx.channel.id !=int(functions.command_channel_list[0]):
    return await ctx.channel.send(bot_messages.command_channel_error)
  if len(channel_list)==0:
    await ctx.channel.send(bot_messages.empty_channels)
    return
  if arg1.isdigit()==True:
    arg1=int(arg1)
  else:
    ctx.channel.send(bot_messages.int_error)
    return

  delete_channels(arg1)
  await ctx.channel.send(bot_messages.channel_deleted)

@Bot.event
async def on_raw_reaction_add(payload): #the work place.
  user = Bot.get_user(payload.user_id)
  guild = Bot.get_guild(payload.guild_id)
  channel = guild.get_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)
  emoji_lists=emoji_list()
  

  if payload.emoji.name in emoji_lists: #checking the reaction emoji is our list or not
    index1=emoji_lists.index(payload.emoji.name) #then getting index of emoji

    for reaction in message.reactions:
      if reaction.emoji == payload.emoji.name: #checking the emoji is in our list or not
        EmojiCount=reaction.count
        if EmojiCount == channel_list[index1][2]: #checking EmojiCount is equal our count or not

          if int(payload.channel_id)!=channel_list[index1][0]: #checking channel id is equal our channel id or not
            return
          if message.author.id == Bot.user.id: #checking messages's owner is bot or not
            return
          for reaction in message.reactions:
            if (reaction.me) and (reaction.emoji == "✅"): #checking the emoji reactioner is bot or not. this is important because bot can't do this 2rd times or much
              return

          else: #then archiving messages according to our channels
            await Bot.get_channel(int(channel_list[index1][1])).send( #it moves messages to selected channel
              "Written by {} :\n\n {}".format(message.author.mention, message.content),
              files=[await f.to_file() for f in message.attachments])
            await Bot.get_channel(int(channel_list[index1][0])).send( #it sends messages channel to say "that messages moved"
              "{} your message moved to this channel --> {}".format(message.author.mention,
                                                                    Bot.get_channel(int(channel_list[index1][1])).mention))
            await message.add_reaction("✅") #then adding a reaction for don't archive message again.
            return

Bot.run("") # you have to add yout bot's token here as a string
