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

login_Url = 'https://sso.donga.ac.kr/svc/tk/Auth.eps?id=studentnew&ac=Y&ifa=N&RelayState=%2fSudExam%2fSUD%2fXSUN0040.aspx&'  # 통합로그인
overnight_Form_Url = 'https://student.donga.ac.kr/SudExam/SUD/XSUN0040.aspx'  # 외박신청

userid = None
passwd = None

now = datetime.datetime.now()
hour = now.hour
minute = now.minute

table_Data = list()
json_Key_List = ['error', 'name', 'student_number', 'at', 'grade', 'department']
json_Result = list()

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

    # login 
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
            driver.get(overnight_Form_Url)

    except Exception as e:
        driver.get(overnight_Form_Url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table_Data = soup.find_all('p', attrs={'class':'basictxtBlu'})
        
        for data_Index in range(len(table_Data[0:6])):
            table_Data[data_Index] = table_Data[data_Index].text
        
        if "대상자가 아닙니다." in str(soup):
            table_Data.insert(0, "-1")
        else: 
            table_Data.insert(0, "1")
            if hour >= 23 and minute >= 30:
                table_Data[0] = "-2"

#######################################################################################################
        json_Result = dict(zip(json_Key_List, table_Data[0:6]))
        
        std_Info_Achievement_Json_Temp = {"overnight_info_result" : json_Result}
        std_Info_Achievement_Json = json.dumps(std_Info_Achievement_Json_Temp,indent=4,ensure_ascii=False)
        print(std_Info_Achievement_Json)