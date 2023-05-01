#Python 3.11.1 (tags/v3.11.1:a7a450f, Dec  6 2022, 19:58:39) [MSC v.1934 64 bit (AMD64)] on win32
#Type "help", "copyright", "credits" or "license()" for more information.
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

def convertTime(timeRange):
    timeRange = timeRange.strip().lower()
    if ":" not in timeRange:
        timeRange = timeRange.replace("pm", ":00pm").replace("am", ":00am")
    hours, minutes = map(int, timeRange[:-2].split(':'))
    if timeRange.endswith('pm'):
        hours += 12
    return hours * 60 + minutes

def timeFormat(mins):
    hours, mins = divmod(mins, 60)
    if hours >= 12:
        ampm = 'pm'
        if hours > 12:
            hours -= 12
    else:
        ampm = 'am'
        if hours == 0:
            hours = 12
    return f"{hours:02d}:{mins:02d}{ampm}"

freeTimes = {}

@bot.command()
async def free(ctx, *, schedule):
    global freeTimes
    time, day = schedule.split(",")
    startTime, endTime = time.strip().lower().split("-")
    startTime = convertTime(startTime)
    endTime = convertTime(endTime)
    day = day.strip().lower()
    user_id = str(ctx.author.id)
    if day not in freeTimes:
        freeTimes[day] = {}
    if startTime not in freeTimes[day]:
        freeTimes[day][startTime] = {}
    freeTimes[day][startTime][user_id] = endTime
    await ctx.send(f"You have been registered as available from {timeFormat(startTime)} to {timeFormat(endTime)} on {day}")

async def on_message(message):
    if message.author == ctx.author:
        return
    if message.content.startswith("!schedule"):
        await schedule(message)

bot.add_listener(on_message)

async def schedule(message):
    time, day, comment = message.content.split(", ")
    time = convertTime(time)
    day = day.strip().lower()
    if day not in freeTimes:
        await message.channel.send(f"There are no users available on {day}.")
        return
    availableUsers = []
    for start_time, users in freeTimes[day].items():
        for user_id, end_time in users.items():
            if start_time <= time < end_time:
                availableUsers.append(user_id)
    if not availableUsers:
        await message.channel.send(f"There are no users available around {timeFormat(time)} on {day}.")
        return
    mention_list = [f'<@{user}>' for user in availableUsers]
    message = f"{', '.join(mention_list)}, you have registered that you are available around this time. {message.author.mention} says \"{comment}\""
    await message.channel.send(message)
    await message.delete()

bot.run(bot token)
