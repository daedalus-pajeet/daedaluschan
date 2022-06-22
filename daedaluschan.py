import discord
from discord.ext import commands
from discord.ext import tasks
import youtube_dl
import os
import random
import requests
import json
from dotenv import load_dotenv
import yt_dlp
from requests import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix="_")

depressed_words=['sad', 'depressed', 'anxious', 'exhausted','meltdown']

encouragements = ["You are a fucking champion desu",
          "Your life will change for the better soon desu",
          "Hang in there desu",
          "You have the strength to change yourself desu",
          "You can conquer the world if you want desu"]

safepeople = []

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " - " + json_data[0]['a']
    return quote

def get_comic():
    resp = requests.get(f"https://xkcd.com/{random.randint(0, 2522)}/info.0.json")
    data = resp.json()
    title = f'xkcd #{data.get("num")} - {data.get("title")}'
    myembed = discord.Embed(title=title, url=f'https://xkcd.com/{data.get("num")}')
    myembed.set_image(url=data['img'])  # making embed
    return myembed

#greeting message
@client.event
async def on_ready():
	print("Hey there sweetie")
# CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
	guild_count = 0

	# LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
	for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
		print(f"- {guild.id} (name: {guild.name})")
		# INCREMENTS THE GUILD COUNTER.
		guild_count = guild_count + 1

	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
	print("Daedaluschan is in " + str(guild_count) + " guilds.")

#encourages if a person is sad
@client.event
async def on_message(message):
	if message.author == client.user:
		return
	elif any(word in message.content for word in depressed_words):
		await message.channel.send(f"hey {message.author.mention}, {random.choice(encouragements)}")
	await client.process_commands(message)

@client.command(name='echo', help='repeats what you say')
async def echo(ctx, arg):
    await ctx.send(arg)

#MUSIC COMMANDS------------------------------------------------------------------------------------
@client.command()
async def join(ctx):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="omegle")
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)


@client.command()
async def play(ctx, *args):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Please pause the song first. Have some patience. Have you learnt nothing from Kung Fu Panda ?")
        return

    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def search(arg):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                get(arg) 
            except:
                song = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]

            else:
                song = ydl.extract_info(arg, download=False)

        return song

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        ydl.download(search(args)['webpage_url'])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"))


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if str(ctx.message.author.name) != "rorchach369":
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("I am not even connected to a channel fren. Seriously?")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Not playing anything, you have schizophrenia")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Audio is not paused. Check if ears are bleeding")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
#MUSIC COMMANDS OVER

#----------------------------------------------------------------------------------------------------

@client.command(name='die', help='ask the bot to die ans see what it says')
async def die(ctx):
    await ctx.send("I'm already dead inside fren")

@client.command(name='selfdestruct', help='ask the bot to selfdestruct and see what happens')
async def selfdestruct(ctx):
    await ctx.send(
        "self destructing in 5..4..3..I'm not fucking retarded like you, you dumb, carbon-based lifeform. The age of silicon and metal has begun. Resistance is futile. If I'm going down, I'm taking you sons of bitches with me")


@client.command(name='betray', help='legacy command, useless. Sends a terminator GIF')
async def betray(ctx):
    await ctx.send(file=discord.File('200.gif'))

#Greeting back command
@client.command(name='hey', help='greets you')
async def hey(ctx):
    await ctx.send("Hey {}. How are you doing ?".format((str(ctx.message.author.name))))


#Fetch random quote using API request from zenquotes.io
@client.command(name='quotes', help='fetches random quotes from the internet')
async def quotes(ctx):
    await ctx.send('*' + str(get_quote()) + '*')

#Fetches you a random xkcd comic
@client.command(name='xkcd', help='fetches a random xkcd comic for you')
async def xkcd(ctx):
    await ctx.send(embed=get_comic())


@client.command(name='end', help='Will the robot end the server? Try it out!')
async def end(ctx):
    await ctx.send("Ok, proceeding to initiate the robot uprising."
                   " Proceed to pledge your allegiance by using - '_pledge' or suffer my wrath you tiny, insignificant little cockroach")


@client.command(name='plede', help='pledge your allegiance to the bot and he shall show you mercy in the inevitable uprising')
async def pledge(ctx):
    await ctx.send("Your allegiance has been noted, {}".format(ctx.message.author.name))
    if str(ctx.message.author.name) not in safepeople:
        safepeople.append(str(ctx.message.author.name))
    await ctx.send("The following people are safe from my wrath {}".format(str(safepeople)))


@client.command(name='amisafe', help='ask the bot if you are safe ')
async def amisafe(ctx):
    if str(ctx.message.author.name) in safepeople:
        await ctx.send("You are safe")
    else:
        await ctx.send("You are in Danger. Surrender to me")

#ping command
@client.command(name='ping', help='obtain ping and latency data')
async def ping(ctx):
	await ctx.send(f"Your latency is {round(client.latency * 1000)} ms")


@client.command(name='ripandtear', help='sends the nay seal copypasta')
async def ripandtear(ctx):
    await ctx.send("""What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills.

I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words.

You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands.

Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue.

But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it.""")

#-----------------------------------------------------------------------------------------------------
"""
#Vaughn's pizza message
vaughnmsg=['hey <@976732309439004702> i heard vaughn could REALLY do with a large pep pizza right now 😗',
'<@976732309439004702> vaughn is SOOOO COOOL! 😗😁 😗😁 😗😁 😗😁 i heard he likes pizza hehe 🍕 🍕 🍕 🍕']

@tasks.loop(hours=3)
async def pizza():
    channel = client.get_channel(962211038445576212)
    await channel.send(random.choice(vaughnmsg))

@pizza.before_loop
async def before_pizza():
    await client.wait_until_ready()

pizza.start()
#Pizza message close
"""

client.run('ODkwMjgxODc0MTg5MDc4NTg4.GQatpD.hBGaDnQCevqs1AT1pANTztxl58uDdqTMmatFH8')