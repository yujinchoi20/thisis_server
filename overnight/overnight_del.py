#!/usr/bin/python3
# -*- coding: utf-8 -*-
# print("Content-type:application/json;charset=utf-8\r\n")

import cgitb
import cgi
import codecs
import sys
import datetime
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

form = cgi.FieldStorage()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
cgitb.enable()

userid = None
passwd = None
year = None
month = None
day = None
tr_Init = None
td_Init = None
json_Result = dict()

login_Url = 'https://sso.donga.ac.kr/svc/tk/Auth.eps?id=studentnew&ac=Y&ifa=N&RelayState=%2fSudExam%2fSUD%2fXSUN0040.aspx&'
calendar_Url = f"https://student.donga.ac.kr/SudExam/SUD/XSUN0120.aspx"
###############################################################################################
try:
    userid = ##
    passwd = ##
    year = 2023
    month = 4
    day = 7
    tr_Init = 3
    date = datetime.date(year, month, 1).weekday() # 0123456 -> 월화수목금토일
    
    # 여기서 저장되는 td_Init의 값은 해당 월의 1일을 나타냄
    if date == 6: #일
        td_Init = 1
    elif date == 0:
        td_Init = 2
    elif date == 1:
        td_Init = 3
    elif date == 2:
        td_Init = 4
    elif date == 3:
        td_Init = 5
    elif date == 4:
        td_Init = 6
    elif date == 5:
        td_Init  =7
except Exception as e:
    json_Result['error'] = "-2"
else:
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=chrome_options)
    driver.implicitly_wait(3)
    driver.get(login_Url)

    driver.find_element(By.ID, 'display_user_id').send_keys(userid) 
    driver.find_element(By.ID, 'display_user_password').send_keys(passwd)
    driver.find_element(By.CLASS_NAME, 'btn_login').click() 

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
        
        json_Result['error'] = "-1" # 기본값
        
        # day+신청중 -> 입력 받은 날짜를 가지고 신청내역이 있는지 확인 
        tr_All = soup.find_all('tr')
        for tr_Idx in range(3, len(tr_All)): #index 1, 2는 년도와 월, 요일이 나와있으므로 확인할 필요x
            for td_Idx in tr_All[tr_Idx]:
                if td_Idx.text == str(day)+"신청중": # day -> 이건 form type이 text인지 number인지 확인이 필요함 
                    try:
                        # tr_Init의 시작은 3, td_Init의 값은 요일에 따라 결정됨. 
                        td_Init = td_Init + int(day) - 1
                        tr_Init = tr_Init + int(td_Init / 7)
                        td_Init = td_Init % 7
                    except Exception as e:
                        json_Result['error'] = "-1"
                    else:
                        # tr, td의 값을 바꿔주면서 입력 받은 날짜를 찾아서 클릭함
                        driver.find_element(By.XPATH, '//*[@id="cal"]/tbody/tr[{tr}]/td[{td}]/a'.format(tr=tr_Init, td=td_Init)).click()
                        # '외박신청 취소' 버튼
                        driver.find_element(By.XPATH, '//*[@id="Button1"]').click()
                        # '외박신청을 취소 하시겠습니까?' alert창
                        alert = driver.switch_to.alert
                        alert.accept()
                        # '취소 완료 하였습니다.' confirm창 
                        confirm = driver.switch_to.alert
                        confirm.accept()
                        json_Result['error'] = "1"
                    
###################################################################################

driver.quit() # 현재 창 뿐만 아니라 나머지 창도 모두 종료 
json_Result = json.dumps({'overnight_info_result': json_Result}, indent=4, ensure_ascii=False)
print(json_Result)