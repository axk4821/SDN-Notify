import requests
from bs4 import BeautifulSoup as bs
import json
import discord
from discord.ext import tasks
import os


def checker():
    #### LINKS USED FOR SDN
    LongSDN = [requests.get("https://forums.studentdoctor.net/threads/2024-2025-ut-san-antonio-long.1493872/page-300").text, "Long"]
    TTULubbockSDN = [requests.get("https://forums.studentdoctor.net/threads/2024-2025-texas-tech-lubbock.1493996/page-100").text, "TTUHSC"]
    BaylorSDN = [requests.get("https://forums.studentdoctor.net/threads/2024-2025-baylor.1494096/page-130").text, "Baylor"]

    contents = [LongSDN, TTULubbockSDN, BaylorSDN]
    recentMessages = {"Long":"", "TTUHSC":"", "Baylor":""}

    ### POSTNUMS.JSON CONTAINS THE MOST RECENT POST NUMBER
    with open("postNums.json", "r") as fil:
        postNums = json.load(fil)

    for cont in contents:
        ### SCRAPES THE RIGHT PARTS USING BS4
        soup = bs(cont[0], 'html.parser')
        div = soup.find_all("div", class_ = "message-inner")[-1]
        msgData = {
            'user' : div.find('div', class_ = "message-userDetails").text.split("\n")[1],
            'time' : div.find('ul', class_ = "message-attribution-main listInline").text.strip(),
            'message' : div.find('article', class_ = "message-body js-selectToQuote").text.strip(),
            'link' : "https://forums.studentdoctor.net" + div.find(lambda tag:tag.name=="a" and "#" in tag.text)['href'],
            'postNumber' : int(div.find(lambda tag:tag.name=="a" and "#" in tag.text).text.strip()[1:]) ### USED TO FILTER OUT THE A TAG AND GET THE ONE WITH THE POUND CHARACTER IN IT
            }
        recentMessages[cont[1]] = msgData
        allNotifs = []
    ### NOTIFICATION ###
    for i in recentMessages:
        if recentMessages[i]["postNumber"] > postNums[i]:
            notification = f'__**{i}**__\n{recentMessages[i]["time"]}\n{recentMessages[i]["user"]}:\n\n>>> {recentMessages[i]["message"]}\n\n{recentMessages[i]["link"]}'

            #### EDITS THE LATEST POST NUMBER AND WRITES TO FILE
            postNums[i] =  recentMessages[i]["postNumber"]
            with open("postNums.json", "w") as fil:
                json.dump(postNums, fil)

            allNotifs.append(notification)
    return(allNotifs)

## DISCORD BOT     
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
intents.message_content = True

notifier = discord.Client(intents=intents)

@notifier.event
async def on_ready():
    await notify.start()


@tasks.loop(seconds=60)
async def notify():
    SDNChannel = notifier.get_channel(1370877007126069388)
    notification = checker()
    if notification:
        for notif in notification:
            await SDNChannel.send(notif)

notifier.run(DISCORD_TOKEN)
