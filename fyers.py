import pandas as pandas
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, datetime
import requests

from INDICATOR import run

def fyers_connect():
    client_id='TYJ1DFBE5G-100'
    secret_key='L6ZICVRYOE'
    redirect_uri="https://trade.fyers.in/api-login/redirect-uri/index.html"
    response_type="code"
    state="sample_state"
    session=fyersModel.SessionModel(client_id=client_id,secret_key=secret_key,redirect_uri=redirect_uri,response_type=response_type)
    respose=session.generate_authcode()
    driver=webdriver.Chrome()
    time.sleep(10)
    driver.get(respose)
    time.sleep(10)

msg_rep=['On 2024-07-04 09:10:00+05:30 BUY WIPRO']
try:
    run()
except requests.exceptions.ChunkedEncodingError:
    run()
