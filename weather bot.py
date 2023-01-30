import requests
import discord
from discord import app_commands
import asyncio
import config
import time

# functions I LOVE STACKOVERFLOW
def deg_to_text(deg):
    return ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"][round(deg/22.5)%16]

async def botexit():
    await asyncio.sleep(5)
    exit()

# Discord bot stuff
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "weather", description = "gets weather from location", guild=discord.Object(id=1044380103427244033))
async def callcommand(interaction: discord.Interaction, city: str, country: str):
    st = time.time()
    openStreetMap = "https://nominatim.openstreetmap.org/search.php?city={}&country={}&format=jsonv2".format(city, country)
    response = requests.get(openStreetMap)
    osmJson = response.json()

    latitude = osmJson[0]["lat"]
    longitude = osmJson[0]["lon"]
    display_name = osmJson[0]["display_name"]
    print(latitude, longitude, display_name)

    url = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&hourly=temperature_2m,relativehumidity_2m,apparent_temperature&daily=temperature_2m_max,temperature_2m_min&current_weather=true&windspeed_unit=mph&timezone=Europe%2FLondon".format(latitude, longitude)
    response = requests.get(url)
    json = response.json()

    temperature = json["current_weather"]["temperature"]
    windspeed = json["current_weather"]["windspeed"]
    winddirection = json["current_weather"]["winddirection"]

    print("Temperature:",temperature,"C")
    print("Wind speed:",windspeed,"mph")
    print("Wind direction:",deg_to_text(winddirection),winddirection, "degrees")
    
    weatherembed = discord.Embed(
    title="Current weather stats for: {}".format(display_name),
    description="Temperature: {}C\n Wind speed: {}mph\n Wind direction: {}, {} Degrees".format(temperature, windspeed, deg_to_text(winddirection), winddirection),
    color=0x87CEEB
    )
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')

    await interaction.response.send_message(embed=weatherembed) #sends the stats embed

@tree.command(name = "shutdown", description = "turns off the bot", guild=discord.Object(id=1044380103427244033))
async def shutdown(interaction):
    await interaction.response.send_message("Shutting down...", delete_after=2.0, ephemeral=True)
    await botexit()



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1044380103427244033))
    print("Online!")

client.run(config.token)