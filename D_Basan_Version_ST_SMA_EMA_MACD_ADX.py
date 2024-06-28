# -*- coding: utf-8 -*-
"""
Strategy description:
    for BUY:
        last three ADX on increment and >20 (current candle + last two)
        MACD signal > previous MACD signal
        MACD > MACD signal
        Super trend at BUY
        EMA 5 > EMA 20
        SMA 50 < EMA 5 & EMA 20
        Buyer % >60
    for SELL:
        last three ADX on increment and >20 (current candle + last two)
        MACD signal < previous MACD signal
        MACD < MACD signal
        Super trend at BUY
        EMA 5 < EMA 20
        SMA 50 > EMA 5 & EMA 20
        Seller % >60  
        
    Target 1% and SL at Super Trend
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
from BASAN_ONLINE import *
from BASAN_CONNECT import *
from INDICATORS import *

NSE_NS=['ACC.NS','ADANIPORTS.NS','AMARAJABAT.NS','APOLLOHOSP.NS','ASIANPAINT.NS','AUROPHARMA.NS','AXISBANK.NS','BALKRISIND.NS','BANDHANBNK.NS','BATAINDIA.NS','BERGEPAINT.NS','BHARATFORG.NS','BHARTIARTL.NS','BIOCON.NS','BPCL.NS','CADILAHC.NS','CENTURYTEX.NS','CIPLA.NS','COLPAL.NS','CONCOR.NS','CUMMINSIND.NS','DABUR.NS','ESCORTS.NS','GLENMARK.NS','GODREJCP.NS','GODREJPROP.NS','GRASIM.NS','HAVELLS.NS','HCLTECH.NS','HDFC.NS','HDFCBANK.NS','HDFCLIFE.NS','HINDPETRO.NS','IBULHSGFIN.NS','ICICIBANK.NS','ICICIPRULI.NS','IGL.NS','INDIGO.NS','INDUSINDBK.NS','INFRATEL.NS','INFY.NS','JUBLFOOD.NS','JUSTDIAL.NS','KOTAKBANK.NS','LICHSGFIN.NS','LT.NS','LUPIN.NS','MARICO.NS','MCDOWELL-N.NS','MFSL.NS','MGL.NS','MINDTREE.NS','MUTHOOTFIN.NS','NIITTECH.NS','PEL.NS','PETRONET.NS','PIDILITIND.NS','PVR.NS','RAMCOCEM.NS','RELIANCE.NS','SBILIFE.NS','SIEMENS.NS','SRTRANSFIN.NS','SUNPHARMA.NS','SUNTV.NS','TATACHEM.NS','TATACONSUM.NS','TATASTEEL.NS','TECHM.NS','TITAN.NS','TORNTPOWER.NS','TVSMOTOR.NS','UBL.NS','UJJIVAN.NS','UPL.NS','VOLTAS.NS','WIPRO.NS']
NSE_STOCK=['ACC','ADANIPORTS','AMARAJABAT','APOLLOHOSP','ASIANPAINT','AUROPHARMA','AXISBANK','BALKRISIND','BANDHANBNK','BATAINDIA','BERGEPAINT','BHARATFORG','BHARTIARTL','BIOCON','BPCL','CADILAHC','CENTURYTEX','CIPLA','COLPAL','CONCOR','CUMMINSIND','DABUR','ESCORTS','GLENMARK','GODREJCP','GODREJPROP','GRASIM','HAVELLS','HCLTECH','HDFC','HDFCBANK','HDFCLIFE','HINDPETRO','IBULHSGFIN','ICICIBANK','ICICIPRULI','IGL','INDIGO','INDUSINDBK','INFRATEL','INFY','JUBLFOOD','JUSTDIAL','KOTAKBANK','LICHSGFIN','LT','LUPIN','MARICO','MCDOWELL-N','MFSL','MGL','MINDTREE','MUTHOOTFIN','NIITTECH','PEL','PETRONET','PIDILITIND','PVR','RAMCOCEM','RELIANCE','SBILIFE','SIEMENS','SRTRANSFIN','SUNPHARMA','SUNTV','TATACHEM','TATACONSUM','TATASTEEL','TECHM','TITAN','TORNTPOWER','TVSMOTOR','UBL','UJJIVAN','UPL','VOLTAS','WIPRO']
NSE_TOKEN=[22,15083,100,157,236,275,5900,335,2263,371,404,422,10604,11373,526,7929,625,694,15141,4749,1901,772,958,7406,10099,17875,1232,9819,7229,1330,1333,467,1406,30125,4963,18652,11262,11195,5258,29135,1594,18096,29962,1922,1997,11483,10440,4067,10447,2142,17534,14356,23650,11543,2412,11351,2664,13147,2043,2885,21808,3150,4306,3351,13404,3405,3432,3499,13538,3506,13786,8479,16713,17069,11287,3718,3787]
NSE_STOCK_DATA={"symbols":NSE_STOCK,
                "token_no":NSE_TOKEN,
                "symbol.NS":NSE_NS}
ns_stock_token=pd.DataFrame(NSE_STOCK_DATA)
ns_stock_token["token_no"]=ns_stock_token["token_no"].astype(int)
ns_stock_token=ns_stock_token.assign(Qty=10)

def run():
    settime=time.localtime()
    cash_po=cash_position_s_fun()
    holdings_completed=order_book_completed()
    if (cash_po<2000)|(settime.tm_hour>=15):
        clearline_1msg("Insufficient fund to process new positions...")
        countdown_timer_MTM(60,portfolio,run)
    else:
        clearline_1msg("Pls wait to generate new calls..")
        holdings_completed=order_book_completed()
        if len(holdings_completed)!=0: 
            Final_Base=pd.merge(ns_stock_token,holdings_completed,how="left",left_on="token_no",right_on="instrument_token",right_index=False,indicator=True)
            Final_Base=Final_Base[Final_Base["_merge"]=="left_only"].drop(['trading_symbol', 'trigger_price', 'instrument_token',
                                                                       'order_side', 'price', 'order_type', 'product', 'oms_order_id','quantity', '_merge'],axis=1)
        else:
            Final_Base=ns_stock_token   
       
    for i, row in Final_Base.iterrows():
        value = row['symbols']
        clearline("Pls wait... validating",value)
        data=Stratergy_one(value,40,3,5,15,30)
        data.columns
        tickers = Ticker(Final_Base.loc[i,"symbol.NS"])
        prices= tickers.price
        LTP_PRICE=prices[Final_Base.loc[i,"symbol.NS"]]["regularMarketPrice"]            
        Final_QTY=[value, Final_Base.loc[i,"token_no"],LTP_PRICE,nse.get_quote(value)["totalBuyQuantity"], nse.get_quote(value)["totalSellQuantity"],Final_Base.loc[i,"Qty"]]
        Final_QTY=pd.DataFrame(Final_QTY)
        Final_QTY=Final_QTY.transpose()
        # Final_QTY=Final_QTY.assign(QTY=np.where(LTP_PRICE < 100, 100,np.where(LTP_PRICE < 200, 75,np.where(LTP_PRICE < 300, 50,np.where(LTP_PRICE < 500, 25,10)))))
        Final_QTY.columns=["SYMBOL","Token_no","LTP","TBQ","TSQ","QTY"]
        Final_QTY=Final_QTY.astype({"SYMBOL":str,"LTP":float,"TBQ":float,"TSQ":float}).fillna(0)
        Final_QTY=Final_QTY.assign(Total_Volume=Final_QTY["TBQ"]+Final_QTY["TSQ"])
        Final_QTY=Final_QTY.assign(TBQ_per=round(((Final_QTY["TBQ"]/Final_QTY["Total_Volume"])*100),2))
        Final_QTY=Final_QTY.assign(TSQ_per=round(((Final_QTY["TSQ"]/Final_QTY["Total_Volume"])*100),2))
        if (Final_QTY.loc[0,"TBQ_per"]>51)&(data.loc[0,"ST_BUY_SELL"]=="BUY") & (data.loc[0,"MACD_SIGNAL"]=="BUY")&(data.loc[0,"SMA_Status"]=="INC"):
            print(Final_QTY.loc[0,"SYMBOL"],Back.GREEN+"-Buyer %:",Final_QTY.loc[0,"TBQ_per"],Back.RED+" - Seller % :",Final_QTY.loc[0,"TSQ_per"])
            print(Style.RESET_ALL)
            print(Back.GREEN+"BUY ",Final_QTY.loc[0,"SYMBOL"],"at",Final_QTY.loc[0,"LTP"],"SL at",data.loc[0,"ST"])
            print(Style.RESET_ALL)
            place_order(client_id,user_order_id,"LIMIT",Final_QTY.loc[0,"Token_no"],Final_QTY.loc[0,"QTY"],Final_QTY.loc[0,"LTP"],data.loc[0,"ST_BUY_SELL"],0)   
           # place_order_SLM(client_id,user_order_id,"SLM",Final_QTY.loc[0,"Token_no"],Final_QTY.loc[0,"QTY"],0,data.loc[0,"ST_BUY_SELL"],data.loc[0,"ST"])
        elif (Final_QTY.loc[0,"TSQ_per"]>51)&(data.loc[0,"ST_BUY_SELL"]=="SELL") & (data.loc[0,"MACD_SIGNAL"]=="SELL")&(data.loc[0,"SMA_Status"]=="DEC"):
            print(Final_QTY.loc[0,"SYMBOL"],Back.GREEN+"-Buyer %:",Final_QTY.loc[0,"TBQ_per"],Back.RED+" - Seller % :",Final_QTY.loc[0,"TSQ_per"])
            print(Style.RESET_ALL)
            print(Back.RED+"SELL ",Final_QTY.loc[0,"SYMBOL"],"at",Final_QTY.loc[0,"LTP"],"SL at",data.loc[0,"ST"])
            print(Style.RESET_ALL)
            place_order(client_id,user_order_id,"LIMIT",Final_QTY.loc[0,"Token_no"],Final_QTY.loc[0,"QTY"],Final_QTY.loc[0,"LTP"],data.loc[0,"ST_BUY_SELL"],0)   
            #place_order_SLM(client_id,user_order_id,"SLM",Final_QTY.loc[0,"Token_no"],Final_QTY.loc[0,"QTY"],0,data.loc[0,"ST_BUY_SELL"],data.loc[0,"ST"])
    countdown(1,run)

def gen_token_info():
    global access_token,client_id,user_order_id
    a_token=input("Do you want to generate ACCESS TOKEN (Y/N):")
    if (a_token=="Y")|(a_token=="y"):
        Connect_Basan("MM1258","aCL9dVHLvR9Bwk18iarWxI11O5RkZNYAz0WbQ4iLy7mGPT78VYbRC2B3Ft15JIcM",25041988)
        user_info=get_access()
        access_token=user_info[0]
        client_id=user_info[1]
        user_order_id=user_info[2]
        run()
    else:
        user_info=get_access()
        access_token=user_info[0]
        client_id=user_info[1]
        user_order_id=user_info[2]
        run()

gen_token_info()

