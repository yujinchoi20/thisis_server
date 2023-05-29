#!/usr/bin/python3
# -*- coding: utf-8 -*-
print("Content-type:text/html;charset=utf-8\r\n")

#######################################################

import sys
import codecs
import cgi
import cgitb
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql
# db 주소 
from db_proc import db

sys.stdout = codecs.getwriter("utf-8") (sys.stdout.detach())
cgitb.enable()

#######################################################

def CLEANUP_DATE_STRING(row_Date):
	row_Clean_List = row_Date.split(".")
	len_Clean_List = len(row_Clean_List)
	date_String = ""
	dotw_List = ['(월)','(화)','(수)','(목)','(금)','(토)','(일)']
	if len_Clean_List == 3 or len_Clean_List == 4:
		date_String += '-'.join(row_Clean_List[:len_Clean_List-1])
		date_String = datetime.strptime(date_String,'%Y-%m-%d')
		dotw_Num = date_String.weekday()
		date_String = date_String.strftime('%Y-%m-%d')
		date_String += dotw_List[dotw_Num]
	else:
		date_String = "ERROR"
	return date_String

def MAKE_DATE_STRING(row_Text):
	row_Text = row_Text.replace("∙","")
	row_Text = row_Text.replace(" ","")
	row_Text = row_Text.replace("\xa0","")
	row_List = row_Text.split("~")
	result_Date_String = ""
	get_Year = row_List[0].split(".")
	pre_Year = get_Year[0]
	row_List[0] = CLEANUP_DATE_STRING(row_List[0])
	if len(row_List) == 2:
		if len(row_List[1].split(".")) == 3:
			row_List[1] = pre_Year + "." + row_List[1]
		row_List[1] = CLEANUP_DATE_STRING(row_List[1])
	result_Date_String += '~'.join(row_List)
	return result_Date_String

def SPLIT_DATE(date):
	result_Date = date.split("-")
	return result_Date

def ERROR_DETECT(calendar_List):
	while "ERROR" in calendar_List:
		error_Idx = calendar_List.index("ERROR")
		list_Length = len(calendar_List)
		if error_Idx == 0:
			next_Date = SPLIT_DATE(calendar_List[error_Idx+1])
			next_Year = next_Date[0]
			next_Month = next_Date[1]
			error_Date = next_Year + '-' + next_Month + "-?"
			calendar_List[error_Idx] = error_Date
		elif error_Idx+1 == list_Length:
			pre_Date = SPLIT_DATE(calendar_List[error_Idx-1])
			pre_Year = pre_Date[0]
			pre_Month = pre_Date[1]
			error_Date = pre_Year + '-' + pre_Month + "-?"
			calendar_List[error_Idx] = error_Date
		else:
			pre_Date = SPLIT_DATE(calendar_List[error_Idx-1])
			next_Date = SPLIT_DATE(calendar_List[error_Idx+1])
			pre_Year = pre_Date[0]
			pre_Month = pre_Date[1]
			next_Year = next_Date[0]
			next_Month = next_Date[1]
			error_Date = pre_Year + '-' + pre_Month + "-?~" + next_Year + '-' + next_Month + "-?"
			calendar_List[error_Idx] = error_Date

#######################################################

cur = db.cursor()

#######################################################

calendar_Url = f"http://www.donga.ac.kr/WebApp/BOARD/BASIC/Read.asp?BIDX=19&CAT=&PG=1&ORD=&KEY=&NUM=7291200&KWD=" 

try:
	response = requests.get(calendar_Url,timeout=(5,5), verify=False) # verify=False 추가 
	response.encoding = None
except requests.exceptions.Timeout:
	error_Sql= # update 테이블 명
	cur.execute(error_Sql)
	db.commit()
	db.close()
	sys.exit()
else:
	html = response.text
	soup = BeautifulSoup(html,'html.parser', from_encoding = 'utf-8')
	calendar_Table = soup.find("table",attrs={"border":"1", "cellspacing":"1", "cellpadding":"3", "width":"99%", "class":"font", "style":"color: #666666; line-height: 20.4px; font-family: 굴림; font-size: 9pt"})
	# print(calendar_Table)

	calendar_Semester_Table = calendar_Table.find_all("tbody")
	
	date_List = []
	schedule_List = []
	semester_List = []

	for semester_Idx in range(len(calendar_Semester_Table)):
		tr_All = calendar_Semester_Table[semester_Idx].find_all("tr")

		if semester_Idx == 0: # 1학기 
			for tr_Idx in range(2, len(tr_All)):
				td_All = tr_All[tr_Idx].find_all("td")
				for td_Idx in range(len(td_All)):
					semester_List.append(1)
					if td_Idx == 0: # 날짜
						# print("date_List : " , MAKE_DATE_STRING(td_All[0].text))
						date_List.append(MAKE_DATE_STRING(td_All[0].text))
					else:
						# print("schedule_List : ", td_All[1].text)
						schedule_List.append(td_All[1].text)


		else: # 2학기 
			for tr_Idx in range(1, len(tr_All)):
				td_All = tr_All[tr_Idx].find_all("td")
				for td_Idx in range(len(td_All)):
					semester_List.append(2)
					if td_Idx == 0: # 날짜
						# print("date_List : " , MAKE_DATE_STRING(td_All[0].text))
						date_List.append(MAKE_DATE_STRING(td_All[0].text))
					else: # 일정
						# print("schedule_List : ", td_All[1].text)
						schedule_List.append(td_All[1].text)

	ERROR_DETECT(date_List)
	sql = "DELETE FROM calendar_info"
	cur.execute(sql)
	db.commit()

	for list_Content_Idx in range(len(date_List)):
		sql = # insert 테이블 명 
		cur.execute(sql)
		db.commit()
db.close()

#######################################################
