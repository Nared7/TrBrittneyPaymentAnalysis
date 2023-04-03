import streamlit as st
import openpyxl as xl
import matplotlib.pyplot as plt
from string import capwords
import json
import gspread
import pandas as pd
import locale


def getInvoiceList():
    # Request All Google Sheet Data to save request limit
    # From this nested dictionary, I will extract the data I need.
    cred_file = r"trbrittneystudentdata-bb3d38df148f.json"
    gc = gspread.service_account(filename=cred_file)
    invoiceWS_List = [sh.title for sh in gc.openall()]
    with open("invoiceList.json", "w") as write_file:
        json.dump(invoiceWS_List, write_file, indent=4, separators=(", ", ": "), sort_keys=True)  # encode dict into JSON

info_data = st.empty()
info_data.write('Load Data from local Database')

try:
    with open('invoiceList.json') as json_file:
        invoiceWS_List = json.load(json_file)
except:
    info_data.write("No Invoice List found. Press 'Fetch Invoice List' to update the database")
    invoiceWS_List = []

# info_data = 'Load Data from local Database'
invoice_option = st.selectbox('Which month would you like to review?', invoiceWS_List)


with open('studentData.json') as json_file:
    allStData = json.load(json_file)
try:
    with open(invoice_option + '.json') as json_file:
        invoice_data = json.load(json_file)
        info_data.write('Local Data loaded from ' + invoice_option)
except:
    info_data.write('No such Invoice Data. Press Fetch to update the database')
    invoice_data = {}

studentData = {}
invoiceData = {}
overDueData = {}
focStudentData = {}

dbStudentList = []
inStudentList = []
focStudentList = []
i = 0
totalIncome = 0
payment = 0
inStudentCount = 0
totalStudent = 0
totalFOC_student = 0


def fetchData():
    global allStData, invoice_data
    cred_file = r"trbrittneystudentdata-bb3d38df148f.json"
    gc = gspread.service_account(filename=cred_file)
    database = gc.open('studentData')
    invoiceWS = gc.open(invoice_option)
    ws_list = database.worksheets()
    invoice_ws = invoiceWS.worksheets()

    for sheet in ws_list:
        list_of_dicts = sheet.get_all_records()

        #       Remove whitespace the data
        for i in range(len(list_of_dicts)):
            list_of_dicts[i] = {x.strip(): v for x, v in list_of_dicts[i].items()}

        allStData[sheet.title] = list_of_dicts

    for sheet in invoice_ws:
        list_of_dicts = sheet.get_all_records()

        #       Remove whitespace the data
        for i in range(len(list_of_dicts)):
            list_of_dicts[i] = {x.strip(): v for x, v in list_of_dicts[i].items()}

        invoice_data[sheet.title] = list_of_dicts


    with open("studentData.json", "w") as write_file:
        json.dump(allStData, write_file, indent=4, separators=(", ", ": "), sort_keys=True)  # encode dict into JSON

    with open(invoice_option + '.json', "w") as write_file:
        json.dump(invoice_data, write_file, indent=4, separators=(", ", ": "), sort_keys=True)  # encode dict into JSON

    with open('studentData.json') as json_file:
        allStData = json.load(json_file)

    with open(invoice_option + '.json') as json_file:
        invoice_data = json.load(json_file)
        info_data.write('Local Data loaded from ' + invoice_option)


st.button('Fetch Data', on_click=fetchData)
st.button('Fetch Invoice List', on_click=getInvoiceList)


def findNumber (inp_str):
    num = ""
    for c in inp_str:
        if c.isdigit():
            num = num + c
    return num

invoiceData.clear()
inStudentCount = 0
for database_className, database_students in invoice_data.items():
    inStudentList.clear()
    totalIncome = 0
    payment = 0
    for database_singleStudent in database_students:
        inStudentCount = inStudentCount + 1
        payment = database_singleStudent['Amount']
        payment = int(findNumber(payment))
        totalIncome = totalIncome + payment
    invoiceData[database_className] = totalIncome


totalStudent = 0
for database_className, database_students in allStData.items():
    for database_singleStudent in database_students:
        totalStudent = totalStudent + 1
        if database_singleStudent['Total Cost (Without Book Fee)'] == "MMK 0" or database_singleStudent['Total Cost (Without Book Fee)'] == " MMK  - ":
            totalFOC_student = totalFOC_student + 1


def convertToCurrency(lst):
    total = 0
    for i in lst:
        total = total + i
    total = "{:,}".format(total)
    return str(total)


st.metric("Total Income", convertToCurrency(list(invoiceData.values())) + " Kyats")

col1, col2, col3 = st.columns(3)
col1.metric("Total Paid Student", inStudentCount)
col2.metric("Total FOC Student", totalFOC_student)
col3.metric("Total Student", totalStudent)

chart_data = pd.DataFrame({
    'Classes': invoiceData.keys(),
    'Kyats': invoiceData.values(),
}).set_index('Classes')
st.bar_chart(chart_data)

