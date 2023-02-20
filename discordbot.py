from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
load_dotenv()
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from discord.ext import commands
from pytz import timezone

datetime.now(timezone('Asia/Seoul'))

PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

def getNwInfoStr(data):
    return "거점명: " + data['area'] + "\n최대인원: " + data['num'] + "\n단계: " + data['stage'] + "\n영지: "+ data['ter']

bot = commands.Bot(command_prefix = '!',intents=discord.Intents.all())

nw_data = pd.read_csv('./bdo_nw_data.csv',encoding='cp949')
today_nws = nw_data[nw_data['date']=="일요일"].astype(str)
today_nw = nw_data
wd = {0:'월요일', 1:'화요일', 2:'수요일',3:'목요일',4:'금요일',5:'토요일', 6:'일요일'}

#bot on ready
@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("AV"))

full_num = 0
crnt_num = 0
np_tdnw = 0
crnt_usr = pd.DataFrame(columns=['name','guild'])
crnt_usr.head(10)

@bot.command()
async def init(ctx):
    return

#send today nord war list (1stage)
@bot.command()
async def setTd(ctx):
    print(datetime.today())
    global today_nws, full_num, np_tdnw, crnt_num
    full_num = 0
    np_tdnw = 0
    crnt_num = 0
    today_nws = nw_data[nw_data['date']==wd[datetime.today().weekday()]].astype(str)
    
    s = [""]
    for i in range(0, today_nws['area'].count()):
        s.append(getNwInfoStr(today_nws.iloc[i]) + "\n--------------")
    d = '```'+'\n'.join(s)+'```'
    embed = discord.Embed(title = '금일 1단 거점 진행 지역 리스트', description =d)
    await ctx.channel.send(embed=embed)

@bot.command()
async def setNw(ctx, arg=None):
    global today_nw, full_num, np_tdnw
    
    if today_nws['date'].iloc[0] != wd[datetime.today().weekday()]:     
        await ctx.channel.send("Err: Today Nord war is not updated! please enter !updateTd")
        return;
    
    if arg == None:
        await ctx.channel.send("Err: No argument. Enter the Nord Name")
        return;
    
    if len(today_nw[today_nw['area'].str.replace(' ','')==arg]) == 0:
        await ctx.channel.send(f"Err: {arg} is not today's Nordwar area")
        return;
    
    today_nw = today_nws[today_nws['area'].str.replace(' ','')==arg]
    await ctx.channel.send(content = "@everyone"+f"{arg} has been set for today's Nordwar", allowed_mentions = discord.AllowedMentions(everyone = True))
    np_tdnw = today_nw.to_numpy()
    full_num = int(np_tdnw[0][2])
    
    s = [""]
    s.append(getNwInfoStr(today_nw.iloc[0]))
    d = '```'+'\n'.join(s)+'```'
    embed = discord.Embed(title = '금일 거점 지역', description =d)
    await ctx.channel.send(embed=embed)
    
    
@bot.command()
async def join(ctx):
    global crnt_num, crnt_usr, full_num
    
    if (crnt_num == full_num) :
        await ctx.channel.send(str(ctx.author.mention + "FULL!"))
        return
    
    usr_name = str(ctx.author.display_name)
    usr_gld = str(ctx.author.display_name)
    usr_name = usr_name.replace(' ', '')
    usr_name = usr_name[usr_name.find(']')+1:]
    usr_gld = usr_gld[usr_gld.find('[')+1:usr_gld.find(']')]
    
    if(crnt_usr['name']==usr_name).any():
        await ctx.channel.send(str(ctx.author.mention + "You've already participated."))
        return
    
    print(usr_name + " Joined")
    crnt_usr.loc[crnt_num] = [usr_name, usr_gld]
    crnt_num = crnt_num+1
    await ctx.channel.send(str(ctx.author.mention + f"{ctx.author.display_name} Thank you! {crnt_num}/{full_num}"))
    print(crnt_usr)

@bot.command()
async def cancle(ctx):
    global crnt_num, crnt_usr, full_num
    
    usr_name = str(ctx.author.display_name)
    usr_name = usr_name.replace(' ', '')
    usr_name = usr_name[usr_name.find(']')+1:]
    usr_n = crnt_usr[crnt_usr['name'] == usr_name].first_valid_index()
    
    if(len(crnt_usr['name'].str.contains(usr_name)) == 0):
        await ctx.channel.send(str(ctx.author.mention + "You didn't participate."))
        return
    
    crnt_num = crnt_num-1
    crnt_usr.drop(usr_n, axis=0, inplace=True)
    crnt_usr.reset_index(inplace=True, drop=True)
    await ctx.channel.send(str(ctx.author.mention + f"{ctx.author.display_name} Oh no.. {crnt_num}/{full_num}"))
    print(crnt_usr)

@bot.command()
async def usrls(ctx):
    global crnt_usr,crnt_num,full_num
    output = crnt_usr.to_numpy()

    s = [f'                    {crnt_num}/{full_num}                    ']
    for data in output:
        s.append(data[0] +'('+data[1]+')')
    d = '```'+'\n'.join(s)+'```'
    embed = discord.Embed(title = '현재 참가자 리스트', description =d)
    await ctx.channel.send(embed=embed)

@bot.command()
async def tdInfo(ctx):
    global today_nw
    s = [""]
    s.append(getNwInfoStr(today_nw.iloc[0]))
    d = '```'+'\n'.join(s)+'```'
    embed = discord.Embed(title = '금일 거점 지역', description =d)
    await ctx.channel.send(embed=embed)

@bot.command()
async def help(ctx):
    global today_nw
    s = [""]
    s.append("!setTd : 오늘자 거점전 초기화")
    s.append("!setNw 거점명 : 오늘자 거점 지역 지정(띄워쓰기 빼고 쓸것)")
    s.append("!join : 오늘자 거점 참여")
    s.append("!cancle : 오늘자 거점 참여 취소")
    s.append("!usrls : 오늘자 거점 참여자 목록")
    s.append("!tdInfo : 오늘자 거점 정보")
    
    d = '```'+'\n'.join(s)+'```'
    embed = discord.Embed(title = '명령어 목록', description =d)
    await ctx.channel.send(embed=embed)

try:
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")