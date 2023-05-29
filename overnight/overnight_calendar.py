#!/usr/bin/python3
# -*- coding: utf-8 -*-
# print("Content-type:application/json;charset=utf-8\r\n")

import sys
import io
import datetime
import json
import cgitb
import cgi
import codecs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

#######################################################
form = cgi.FieldStorage()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
cgitb.enable()
#######################################################
userid = None
passwd = None
year = str(datetime.datetime.now().year)
month = str(datetime.datetime.now().month)

json_Result = list()
dateList = list()
flagList = list()

login_Url = 'https://sso.donga.ac.kr/svc/tk/Auth.eps?id=studentnew&ac=Y&ifa=N&RelayState=%2fSudExam%2fSUD%2fXSUN0040.aspx&' 
calendar_Url = f"https://student.donga.ac.kr/SudExam/SUD/XSUN0120.aspx"
#######################################################################################################

try:
    userid = ##
    passwd = ##
except Exception as e:
    json_Result['error'] = "-2"     
else:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1980x1080')
    chrome_options.add_argument('disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=Service('./chromedriver'), options=chrome_options)
    driver.implicitly_wait(3)
    driver.get(login_Url)
    driver.find_element(By.ID, 'display_user_id').send_keys(userid)
    driver.find_element(By.ID, 'display_user_password').send_keys(passwd)
    driver.find_element(By.CLASS_NAME, 'btn_login').click()  # login btn
        
    try:
        alert = driver.switch_to.alert
        if "대상자가 아닙니다." in alert.text:
            json_Result['error'] = "-1"
        alert.accept
        
        if "3개월동안 비밀번호를 변경하지 않아 [비밀번호 변경 페이지]로 바로 넘어갑니다." in alert.text:
            alert.accept
            driver.get(calendar_Url)
            
    except Exception as e:
        driver.get(calendar_Url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find("table", attrs={"id":"cal"})
        tds = table.find_all('td')
        if int(month) < 10:
            month = "0" + month
            
        date = ""
        dateFlag = ""
        for td in tds:
            if "신청중" in td.text:
                # dateFlag = "신청중"
                # day = td.text.rstrip("신청중")
                # if int(day) < 10:
                #     day = "0" + str(day)
                # date = f"{year}-{month}-{day}"
                
                # dateList.append(date)
                # flagList.append(dateFlag)
                print(td.find("a").text)
                
            elif "외박" in td.text:
                # dateFlag = "외박"
                # day = td.text.rstrip("외박")
                # if int(day) < 10:
                #     day = "0" + str(day)
                # date = f"{year}-{month}-{day}"
                
                # dateList.append(date)
                # flagList.append(dateFlag)
                print(td.find("span").id)
                
#############################################################################################################
    json_Result = dict(zip(dateList, flagList))

    std_Info_Achievement_Json_Temp = {"overnight_info_result" : json_Result}
    std_Info_Achievement_Json = json.dumps(std_Info_Achievement_Json_Temp,indent=4,ensure_ascii=False)
    # print(std_Info_Achievement_Json)