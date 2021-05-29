import discord
import os
import json
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, MissingRequiredArgument
from keep_alive import keep_alive

client = commands.Bot(command_prefix = "+")

@client.event
async def on_ready():
  print("1, 2, 3, 4, 5, 6, 7, 8, 9, 10!")

@client.event
async def on_guild_join(guild):
  for channel in guild.text_channels:
    if channel.permissions_for(guild.me).send_messages:
      embed=discord.Embed(title="Thanks for inviting!", description="Counting +1", color=0x00ff00)
      embed.set_author(name="Counting +1", icon_url="https://discord.com/assets/0e291f67c9274a1abdddeb3fd919cbaa.png")
      embed.add_field(name="Hi! Thanks for adding me to your server!", value="To start counting, please use `# config[channel]` to locate your counting channel!", inline=False)
      embed.set_footer(text="Start the count!")
      await channel.send(embed=embed)
      break

client.remove_command("help")

@client.command()
async def help(ctx):
  embed=discord.Embed(title="Help has arrived!", description="# help", color=client.user.color)
  embed.set_author(name="Counting +1", icon_url="https://discord.com/assets/0e291f67c9274a1abdddeb3fd919cbaa.png")
  embed.add_field(name="Game", value="# server: Checks the server stats", inline=False)
  embed.add_field(name="Bot", value="# help: Sends a message to help you\n# # invite: Makes an invite for this bot", inline=False)
  embed.add_field(name="Setings", value="# channel: Sets the counting channel\n#config: Toggles the bot's ability. Default is off.", inline=False)
  embed.set_footer(text=f"Requsted by {ctx.author}")
  await ctx.send(embed=embed)

@client.command()
async def invite(ctx):
  await ctx.send("https://discord.com/api/oauth2/authorize?client_id=824266782344478740&permissions=8&scope=bot")

@client.command()
@has_permissions(manage_guild=True)
async def channel(ctx, channel):
  with open("count.json", "r") as f:
    count_json = json.load(f)
  if channel == None:
    channel = f"<#{ctx.channel.id}>"

  if str(ctx.guild.id) not in count_json:
    count_json["guilds"][str(ctx.guild.id)] = {
      "channel": str(channel),
      "mode": "off",
      "current_count": {"count_num":0,"last_poster": str(client.user.id)},
      "best_count": 0
    }
  else:
    count_json["guilds"][str(ctx.guild.id)]["channel"] = str(channel)
  with open("count.json", "w") as f:
    json.dump(count_json, f, indent=2)
  await ctx.send(f"Successfully made {channel} your counting channel.")

@client.command()
@has_permissions(manage_guild=True)
async def config(ctx, text):
  true_list = ["on", "true", "yes", "y", "enable"]
  false_list = ["off", "false", "no", "n", "disable"]
  with open("count.json", "r") as f:
    count_json = json.load(f)
  if text.casefold() in true_list:
    count_json["guilds"][str(ctx.guild.id)]["mode"] = "on"
    await ctx.send("Counting +1 is now enabled in your server.")
  elif text.casefold() in false_list:
    count_json["guilds"][str(ctx.guild.id)]["mode"] = "off"
    await ctx.send("Counting +1 is now disabled in your server.")
  else:
    await ctx.send("Please use one of these: ```on/off\ntrue/false\nyes/no\ny/n\nenable/disable```")
  with open("count.json", "w") as f:
    json.dump(count_json, f, indent=2)

@client.command()
async def stats(ctx):
  with open("count.json", "r") as f:
    count_json = json.load(f)
  server_stat = count_json["guilds"][str(ctx.guild.id)]
  embed=discord.Embed(title=f"Stats of {ctx.guild}", color=ctx.author.color)
  embed.set_thumbnail(url=ctx.guild.icon_url)
  embed.add_field(name="Current Count", value=server_stat["current_count"]["count_num"], inline=False)
  embed.add_field(name="Best Count", value=server_stat["best_count"], inline=False)
  await ctx.send(embed=embed)
    

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  with open("count.json", "r") as f:
    count_json = json.load(f)
  if str(message.guild.id) in count_json["guilds"]:
    guild_info = count_json["guilds"][str(message.guild.id)]
    if guild_info["channel"] == f"<#{str(message.channel.id)}>": #checks if it is in the right channel. If it isn't, it will be ignored.
      if guild_info["mode"] == "on":
        if type(int(message.content)) == int:
          if guild_info["current_count"]["last_poster"] != str(message.author.id): #if both posters are same
            if guild_info["current_count"]["count_num"] + 1 == int(message.content): #checks if the count is right
              await message.add_reaction("✅")
              guild_info["current_count"]["count_num"] += 1
              guild_info["current_count"]["last_poster"] = str(message.author.id)
              if guild_info["current_count"]["count_num"] > guild_info["best_count"]: #did it break the highscore
                guild_info["best_count"] = guild_info["current_count"]["count_num"]
            else:
              await message.channel.send("Uh, did you pass first grade? You can't even do basic math.")
              guild_info["current_count"]["count_num"] = 0
              guild_info["current_count"]["last_poster"] = client.user.id
          else:
            await message.channel.send("'-' No doubleposting!")
            guild_info["current_count"]["last_poster"] = client.user.id
        with open("count.json", "w") as f:
          json.dump(count_json, f, indent=2)
  await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound) or isinstance(error, ValueError):
    pass
  else:
    if isinstance(error, commands.CheckFailure):
      await ctx.send("Hey. You don't have the permissions.")
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("Ayy. Your arguments ain't right.")
    else:
      await ctx.send(f"An error occured! ```{error}```")
    raise error

keep_alive()
client.run(os.getenv("TOKEN"))
