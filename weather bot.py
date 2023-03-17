import requests
import discord
from discord import app_commands
from discord.app_commands import Choice
import asyncio
import config
import time
import weather_codes

#I love stackoverflow
def deg_to_text(deg):
    return ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"][round(deg/22.5)%16]

# Discord bot stuff
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "weather", description = "gets weather from location", guild=discord.Object(id=config.guildid))

@app_commands.describe(
    city = "inputted city",
    country = "inputted country",
    unit = "Default set to Celcius" #this will be changable in a settings command sometime in the future
)

@app_commands.choices(unit = [
    Choice(name = "Celcius", value="celcius"),
    Choice(name = "Fahrenheit", value="fahrenheit")
])

async def callcommand(interaction: discord.Interaction, city: str, country: str, unit: str="Celcius"):
        
    st = time.time()
    openStreetMap = "https://nominatim.openstreetmap.org/search.php?city={}&country={}&format=jsonv2".format(city, country)
    response = requests.get(openStreetMap)
    osmJson = response.json()

    latitude = osmJson[0]["lat"]
    longitude = osmJson[0]["lon"]
    display_name = osmJson[0]["display_name"]
    print(latitude, longitude, display_name)

    url = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&hourly=temperature_2m,relativehumidity_2m,apparent_temperature&daily=temperature_2m_max,temperature_2m_min&current_weather=true&windspeed_unit=mph&timezone=auto".format(latitude, longitude)
    response = requests.get(url)
    json = response.json()

    temperature = json["current_weather"]["temperature"]
    windspeed = json["current_weather"]["windspeed"]
    winddirection = json["current_weather"]["winddirection"]
    localtime = json["current_weather"]["time"]
    weathercode = json["current_weather"]["weathercode"]
    weatherdescription = weather_codes.get_weather_description(weathercode)
    generationtime = json["generationtime_ms"]
    
    if unit == "fahrenheit":
        temperature = (temperature * 9 / 5) + 32
        unit = "Fahrenheit"
    else:
        unit = "Celsius"
         
    print("Temperature:",temperature,"C")
    print("Wind speed:",windspeed,"mph")
    print("Wind direction:",deg_to_text(winddirection),winddirection, "degrees")
    print(localtime)
    print("Generation time: ",generationtime)
    print(weatherdescription)
    
    weatherembed = discord.Embed(
    title="Current weather stats for: {}".format(display_name),
    description="**Current local time in: {}\n**{}\n\n {}\nTemperature: {} {}\n Wind speed: {}mph\n Wind direction: {}, {} Degrees\n\n API Response time: {:0.2f} Seconds".format(city.capitalize(), localtime, weatherdescription, temperature, unit, windspeed, deg_to_text(winddirection), winddirection, generationtime),
    color=0x87CEEB
    )
    
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')

    await interaction.response.send_message(embed=weatherembed) #sends the stats embed

@tree.command(name = "shutdown", description = "turns off the bot", guild=discord.Object(id=config.guildid))
async def shutdown(interaction):
    await interaction.response.send_message("Shutting down...", delete_after=2.0, ephemeral=True)
    await print("Bot offline")
    await client.close()

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=config.guildid))
    print("Online!")

client.run(config.token)