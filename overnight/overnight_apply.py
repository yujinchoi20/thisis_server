# #!/usr/bin/python3
# # -*- coding: utf-8 -*-
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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert

def check_Exists_By_XPATH(xpath):
    try:
        Select(driver.find_element(By.XPATH, xpath))
    except Exception as e: 
        return False
    return True

form = cgi.FieldStorage()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
cgitb.enable()
###############################################################################################

userid = None
passwd = None
ddl_place = None
ddlYear1 = None
ddlMonth1 = None
ddlDay1 = None
ddlYear2 = None
ddlMonth2 = None
ddlDay2 = None
json_Result = dict()

login_Url = 'https://sso.donga.ac.kr/svc/tk/Auth.eps?id=studentnew&ac=Y&ifa=N&RelayState=%2fSudExam%2fSUD%2fXSUN0040.aspx&'  #통합로그인
overnight_Form_Url = 'https://student.donga.ac.kr/SudExam/SUD/XSUN0040.aspx'  #외박신청

now = datetime.datetime.now()
hour = now.hour
minute = now.minute

###############################################################################################

if hour >= 23 and minute >= 30:
    json_Result['error'] = "-6"

else:
    try:
        # userid = form['userid'].value
        # passwd = form['passwd'].value
        # ddl_place = form['ddl_place'].value
        # ddlYear1 = int(form['ddlYear1'].value)
        # ddlMonth1 = int(form['ddlMonth1'].value)
        # ddlDay1 = int(form['ddlDay1'].value)
        # ddlYear2 = int(form['ddlYear2'].value)
        # ddlMonth2 = int(form['ddlMonth2'].value)
        # ddlDay2 = int(form['ddlDay2'].value)
        
    except Exception as e:
        json_Result['error'] = "-2" 
    else:
        # selenium version 4.8.0
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(
            './chromedriver.exe'), options=chrome_options)
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
            # url 변경
            driver.get(overnight_Form_Url)
            ddl_Chk = check_Exists_By_XPATH('//*[@id="ddl_place"]')

            if ddl_Chk:
                # place
                ddl_Place = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddl_place"]'))
                ddl_Place.select_by_visible_text(str(ddl_place))

                # date
                ddl_Year1 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlYear1"]'))
                ddl_Month1 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlMonth1"]'))
                ddl_Day1 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlDay1"]'))
                ddl_Year2 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlYear2"]'))
                ddl_Month2 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlMonth2"]'))
                ddl_Day2 = Select(driver.find_element(
                    By.XPATH, '//*[@id="ddlDay2"]'))
                ddl_Year1.select_by_value(str(ddlYear1))
                ddl_Month1.select_by_value(str(ddlMonth1))
                ddl_Day1.select_by_value(str(ddlDay1))
                ddl_Year2.select_by_value(str(ddlYear2))
                ddl_Month2.select_by_value(str(ddlMonth2))
                ddl_Day2.select_by_value(str(ddlDay2))
                
                #submit
                driver.find_element(By.NAME, 'ImageButton1').click()
                
                try:
                    alert = driver.switch_to.alert
                    if "중복" in alert.text:
                        json_Result['error'] = "-3"
                    elif "대상자" in alert.text:
                        json_Result['error'] = "-1"
                    else:
                        json_Result['error'] = alert.text
                    alert.accept
                except Exception as e:
                    html = driver.page_source
                    if "정상적으로 완료되었습니다" in html:
                        json_Result['error'] = "1"
                    elif "작을 수 없습니다" in html:
                        json_Result['error'] = "-4"
                    else:
                        json_Result['error'] = "-5"
            
            else:
                json_Result['error'] = "-7" # 외박신청 기간 아님
        ###############################################################################################

        driver.quit()
json_Result = json.dumps(
    {'overnight_info_result': json_Result}, indent=4, ensure_ascii=False)
print(json_Result)
