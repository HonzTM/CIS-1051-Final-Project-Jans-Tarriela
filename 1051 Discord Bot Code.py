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

@bot.command(name = "hello", description ="This is a command")
async def hello(ctx):
    await ctx.send("Hello!")

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

@bot.command()
async def schedule(ctx, *, when):
    time, day, comment = when.split(", ")
    time = convertTime(time)
    day = day.strip().lower()
    if day not in freeTimes:
        await ctx.send(f"There are no users available on {day}.")
        return
    availableUsers = []
    for start_time, users in freeTimes[day].items():
        for user_id, end_time in users.items():
            if start_time <= time < end_time:
                availableUsers.append(user_id)
    if not availableUsers:
        await ctx.send(f"There are no users available around {timeFormat(time)} on {day}.")
        return
    message = f"{', '.join(f'<@{user}>' for user in availableUsers)}, you have registered that you are available around this time. {ctx.author.mention} says \"{comment}\""
    await ctx.send(message)
    await ctx.message.delete()
    
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if "ping" in message.content.lower():
        await message.channel.send("pong!")

bot.run(bot token here)
