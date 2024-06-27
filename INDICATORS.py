# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 15:54:36 2020

@author: BibeeshYS
"""


import sys
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import pandas as pd
import time
from colorama import Fore, Back, Style, init
from termcolor import colored, cprint
from datetime import date, timedelta, datetime
from yahooquery import Ticker
from pandas_datareader import data as wb
from nsetools import Nse
nse=Nse()
from nsepy import get_history
import stockstats
from stockstats import StockDataFrame

def Super_Trend_SMA_EMA_MACD_ADX_PIVOT(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA,Period,Interval):
    data =yf.download(Stock_name+".NS", period=Period,interval=Interval,progress=False)
    data.columns=["open","high","low","close","amount","volume"]
    data=StockDataFrame(data)
    data.get('boll')
    data.get('adx')
    data.get("macd")
    data=data.assign(sma_50=data["close"].rolling(50).mean())
    data=pd.DataFrame(data)
    data=data.reset_index()

    data=data.assign(BUB=0.00)
    data=data.assign(BLB=0.00)
    data=data.assign(FUB=0.00)
    data=data.assign(FLB=0.00)
    data=data.assign(ST=0.00)
    data=data.assign(ATR=data["tr"].rolling(Supertrend_period).mean())
    data=data.assign(ATR= data["ATR"].replace('nan', np.nan).fillna(0))                                      
    data=data.assign(BUB= round(((data["high"] + data["low"]) / 2) + (Supertrend_length * data["ATR"]),2))
    data=data.assign(BLB= round(((data["high"] + data["low"]) / 2) - (Supertrend_length * data["ATR"]),2))
    data=data.assign(FUB = data["FUB"].replace('nan', np.nan).fillna(0))

    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FUB"]=0.00
        else:
            if (data.loc[i,"BUB"]<data.loc[i-1,"FUB"])|(data.loc[i-1,"close"]>data.loc[i-1,"FUB"]):
                data.loc[i,"FUB"]=data.loc[i,"BUB"]
            else:
                data.loc[i,"FUB"]=data.loc[i-1,"FUB"]
    
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FLB"]=0.00
        else:
            if (data.loc[i,"BLB"]>data.loc[i-1,"FLB"])|(data.loc[i-1,"close"]<data.loc[i-1,"FLB"]):
                data.loc[i,"FLB"]=data.loc[i,"BLB"]
            else:
                data.loc[i,"FLB"]=data.loc[i-1,"FLB"]               
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"ST"]=0.00
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"]) & (data.loc[i,"close"]<=data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"])&(data.loc[i,"close"]>data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]>=data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]<data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]

    for i, row in data.iterrows():
       if i<=2:
           data.loc[i,"ema_5"]=0.00
           data.loc[i,"ema_20"]=0.00
       else:
           data.loc[i,"ema_5"]=data.loc[i,"close"]*(2/(EMA_1+1))+data.loc[i-1,"ema_5"]*(1-(2/(EMA_1+1)))
           data.loc[i,"ema_20"]=data.loc[i,"close"]*(2/(EMA_2+1))+data.loc[i-1,"ema_20"]*(1-(2/(EMA_2+1)))          
    
    for i, row in data.iterrows():
        if i==0:
            data["ST_BUY_SELL"]="NA"
        elif (data.loc[i,"ST"]<data.loc[i,"close"]) :
            data.loc[i,"ST_BUY_SELL"]="BUY"
            data.loc[i,"SL"]=data.loc[i,"sma_50"]-1.5
        else:
            data.loc[i,"ST_BUY_SELL"]="SELL"
            data.loc[i,"SL"]=data.loc[i,"sma_50"]+1.5
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"adx_20"]="NO"
        elif (data.loc[i,"adxr"]>20) & (data.loc[i,"adxr"]>data.loc[i-1,"adxr"]) & (data.loc[i-1,"adxr"]>data.loc[i-2,"adxr"]):
            data.loc[i,"adx_20"]="YES"
        else:
            data.loc[i,"adx_20"]="NO"
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"macd_buy_sell"]="NO"
        elif (data.loc[i,"macds"]>data.loc[i-1,"macds"]) & (data.loc[i,"macd"]>data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="BUY"
        elif (data.loc[i,"macds"]<data.loc[i-1,"macds"]) & (data.loc[i,"macd"]<data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="SELL"    
    data["PP"]=round((data[["high","low","close"]].sum(axis=1))/3,1).shift()
    data["R1"]=round((data["PP"]*2)-(data["low"]).shift(),1)
    data["R2"]=round(data["PP"]+(data["high"]-data["low"]).shift(),1)
    data["R3"]=round((data["high"]).shift()+(2*(data["PP"]-(data["low"].shift()))),1)
    data["S1"]=round((2*data["PP"])-(data["high"]).shift(),1)
    data["S2"]=round(data["PP"]-(data["high"]-data["low"]).shift(),1)
    data["S3"]=round((data["low"]).shift()-2*((data["high"]).shift()-data["PP"]),1)
    data=round(data,1)
    SuperTrend=data.iloc[75:]#[["ST_BUY_SELL","Close","ST"]]#.tail(1)
    data=data[['Datetime', 'open', 'high', 'low', 'close', 'boll', 'boll_ub', 'boll_lb','adx',
       'adxr', 'sma_50', 'ST','ST_BUY_SELL', 'adx_20', 'ema_5', 'ema_20',"SL","macd_buy_sell",'PP', 'R1', 'R2',
       'R3', 'S1', 'S2', 'S3']]
    data=round(data.reset_index(inplace=False).drop(["index"],axis=1),1) 
    return(data)    


def Stratergy_one(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA):
    global SuperTrend
    data =yf.download(Stock_name+".NS", period="2d",interval="5m",progress=False)
    data.columns=["open","high","low","close","amount","volume"]
    data=StockDataFrame(data)
    data.get('boll')
    data.get('adx')
    data.get("macd")
    data=data.assign(Symbol=Stock_name)
    data=pd.DataFrame(data)
    data=data.reset_index()
    data=data.assign(sma_value=data["close"].rolling(SMA).mean())
    for i, row in data.iterrows():
        if i<=2:
            data.loc[i,"sma_status"]="NA"
        elif (data.loc[i,"sma_value"]>data.loc[i-1,"sma_value"])&(data.loc[i-1,"sma_value"]>data.loc[i-2,"sma_value"]):
            data.loc[i,"sma_status"]="INC"
        elif (data.loc[i,"sma_value"]<data.loc[i-1,"sma_value"])&(data.loc[i-1,"sma_value"]<data.loc[i-2,"sma_value"]):
            data.loc[i,"sma_status"]="DEC"
        else:
            data.loc[i,"sma_status"]="NA"
    data=data.assign(tr0 = abs(data["high"] - data["low"]))
    data=data.assign(tr1 = abs(data["high"] - data["close"].shift(1)))
    data=data.assign(tr2= abs(data["low"]- data["close"].shift(1)))
    data=data.assign(TR = round(data[['tr0', 'tr1', 'tr2']].max(axis=1),2))
    
    # data["ATR"]=0.00
    data=data.assign(BUB=0.00)
    data=data.assign(BLB=0.00)
    data=data.assign(FUB=0.00)
    data=data.assign(FLB=0.00)
    data=data.assign(ST=0.00)
    data=data.assign(ATR=data["TR"].rolling(Supertrend_period).mean())
    data=data.assign(ATR= data["ATR"].replace('nan', np.nan).fillna(0))                                      
    data=data.assign(BUB= round(((data["high"] + data["low"]) / 2) + (Supertrend_length * data["ATR"]),2))
    data=data.assign(BLB= round(((data["high"] + data["low"]) / 2) - (Supertrend_length * data["ATR"]),2))
    data=data.assign(FUB = data["FUB"].replace('nan', np.nan).fillna(0))

    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FUB"]=0.00
        else:
            if (data.loc[i,"BUB"]<data.loc[i-1,"FUB"])|(data.loc[i-1,"close"]>data.loc[i-1,"FUB"]):
                data.loc[i,"FUB"]=data.loc[i,"BUB"]
            else:
                data.loc[i,"FUB"]=data.loc[i-1,"FUB"]
    
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FLB"]=0.00
        else:
            if (data.loc[i,"BLB"]>data.loc[i-1,"FLB"])|(data.loc[i-1,"close"]<data.loc[i-1,"FLB"]):
                data.loc[i,"FLB"]=data.loc[i,"BLB"]
            else:
                data.loc[i,"FLB"]=data.loc[i-1,"FLB"]               
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"ST"]=0.00
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"]) & (data.loc[i,"close"]<=data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"])&(data.loc[i,"close"]>data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]>=data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]<data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]

    for i, row in data.iterrows():
       if i<=2:
           data.loc[i,"ema_1"]=0.00
           data.loc[i,"ema_2"]=0.00
       else:
           data.loc[i,"ema_1"]=data.loc[i,"close"]*(2/(EMA_1+1))+data.loc[i-1,"ema_1"]*(1-(2/(EMA_1+1)))
           data.loc[i,"ema_2"]=data.loc[i,"close"]*(2/(EMA_2+1))+data.loc[i-1,"ema_2"]*(1-(2/(EMA_2+1)))          
    
    for i, row in data.iterrows():
        if i==0:
            data["ST_BUY_SELL"]="NA"
        elif (data.loc[i,"ST"]<data.loc[i,"close"]) :
            data.loc[i,"ST_BUY_SELL"]="BUY"
            data.loc[i,"SL"]=data.loc[i,"sma_value"]-1.5
        else:
            data.loc[i,"ST_BUY_SELL"]="SELL"
            data.loc[i,"SL"]=data.loc[i,"sma_value"]+1.5

    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"ADX_STATUS"]="NO"
        elif (data.loc[i,"adxr"]>20) & (data.loc[i,"adxr"]>data.loc[i-1,"adxr"]) & (data.loc[i-1,"adxr"]>data.loc[i-2,"adxr"]):
            data.loc[i,"ADX_STATUS"]="YES"
        else:
            data.loc[i,"ADX_STATUS"]="NO"
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"macd_buy_sell"]="NO"
        elif (data.loc[i,"macds"]>data.loc[i-1,"macds"]) & (data.loc[i,"macd"]>data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="BUY"
        elif (data.loc[i,"macds"]<data.loc[i-1,"macds"]) & (data.loc[i,"macd"]<data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="SELL"  
            
    data=data.assign(VWAP=(data[["high","low","close"]].mean(axis=1)*data["volume"])/data["volume"])
    data=round(data,1)
    data=data.iloc[75:]#[["ST_BUY_SELL","Close","ST"]]#.tail(1)
    data=data[['Datetime', 'open', 'high', 'low', 'close', 'amount', 'volume',
       'Symbol','ST','ST_BUY_SELL','ema_1', 'ema_2', 'sma_value','sma_status', 'SL',
       'macd_buy_sell', 'VWAP','ADX_STATUS']]
    data.columns=['Datetime', 'open', 'high', 'low', 'close', 'amount', 'volume',
           'Symbol','ST_Line','ST_BUY_SELL', 'EMA_1', 'EMA_2','SMA', 'SMA_Status','SMA_SL',"MACD_SIGNAL","VWAP","ADX_STATUS"]
    tickers = Ticker(Stock_name+".NS")
    prices= tickers.price
    LTP_PRICE=prices[Stock_name+".NS"]["regularMarketPrice"]
    if (data.iloc[-2:,9]=="BUY").all() & (data.iloc[-5:-2,9]=="SELL").all() & (data.iloc[-1,10]>data.iloc[-1,11]) & (data.iloc[-1,12]<data.iloc[-1,10])& (data.iloc[-1,12]<data.iloc[-1,11]) & (data.iloc[-1,13]=="INC"): 
        ST_BB=[LTP_PRICE,data.iloc[-1,9],data.iloc[-1,8],data.iloc[-1,10],data.iloc[-1,11],data.iloc[-1,12],data.iloc[-1,13],data.iloc[-1,14],"BUY",data.iloc[-2,15],data.iloc[-2,16],data.iloc[-2,17]]
    elif (data.iloc[-2:,9]=="SELL").all() & (data.iloc[-5:-2,9]=="BUY").all() & (data.iloc[-1,10]<data.iloc[-1,11]) & (data.iloc[-1,12]>data.iloc[-1,10]) & (data.iloc[-1,12]>data.iloc[-1,11])& (data.iloc[-1,13]=="DEC") :
        ST_BB=[LTP_PRICE,data.iloc[-1,9],data.iloc[-1,8],data.iloc[-1,10],data.iloc[-1,11],data.iloc[-1,12],data.iloc[-1,13],data.iloc[-1,14],"SELL",data.iloc[-2,15],data.iloc[-2,16],data.iloc[-2,17]]
    else:
        ST_BB=[LTP_PRICE,"NA",data.iloc[-1,8],data.iloc[-1,10],data.iloc[-1,11],data.iloc[-1,12],data.iloc[-1,13],data.iloc[-1,14],"NA",data.iloc[-2,15],data.iloc[-2,16],data.iloc[-2,17]]
    Result=pd.DataFrame(ST_BB).transpose()
    Result.columns=["LTP","ST_BUY_SELL","ST","EMA_1","EMA_2","SMA","SMA_Status","SMA_SL","BUY_SELL","MACD_SIGNAL","VWAP","ADX_STATUS"]
    Result=Result.astype({"LTP":float,"ST_BUY_SELL":str,"ST":float,"EMA_1":float,"EMA_2":float,"SMA":float,"SMA_Status":str,"SMA_SL":float,"BUY_SELL":str,"MACD_SIGNAL":str,"VWAP":float,"ADX_STATUS":str})
    return(Result)


def color_red_green(val):
    if val < 0:
        # color = Fore.RED
        color = Back.RED
    else:
        # color = Fore.GREEN
        color = Back.GREEN
    return color  + str('{0:0}'.format(val))+ Style.RESET_ALL

def clearline_1msg(msg):
    CURSOR_UP_ONE = '\033[K'
    ERASE_LINE = '\x1b[2K'
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE+"\r")
    print(msg, end='                                                 \r')
   


def clearline(msg,msg2):
    CURSOR_UP_ONE = '\033[K'
    ERASE_LINE = '\x1b[2K'
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE+'\r')
    print(msg,msg2, end='                                                 \r')


def countdown_timer_MTM(t,calling_function1,calling_function2):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        clearline(calling_function1(),timer)
        # print(Target_Base[["SYMBOL","TGT"]])        
        t -= 5
        time.sleep(5)
        # print("\033[H\033[J")    
    calling_function2()

def countdown(t,calling_function):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        clearline_1msg(timer)        
        t -= 1
        time.sleep(1)
        # print("\033[H\033[J")
    calling_function()    
