import streamlit as st
import openpyxl as xl
import matplotlib.pyplot as plt
from string import capwords
import json
import gspread
import pandas as pd

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

studentData.clear()
for database_className, database_students in allStData.items():
    dbStudentList.clear()
    focStudentList.clear()
    for database_singleStudent in database_students:
        name = database_singleStudent['Myanmar Name']
        name = name.strip()
        name = name.lower()
        dbStudentList.append(name)

        if database_singleStudent['Total Cost (Without Book Fee)'] == "MMK 0" or database_singleStudent['Total Cost (Without Book Fee)'] == " MMK  - ":
            focStudentList.append(name)
    studentData[database_className] = dbStudentList.copy()
    focStudentData[database_className] = focStudentList.copy()


invoiceData.clear()
for database_className, database_students in invoice_data.items():
    inStudentList.clear()
    for database_singleStudent in database_students:
        name = database_singleStudent['Student Name']
        name = name.strip()
        name = name.lower()
        inStudentList.append(name)
    invoiceData[database_className] = inStudentList.copy()



for className in studentData:
    paidStudent = invoiceData.get(className)
    totalStudent = studentData.get(className)
    focStudent = focStudentData.get(className)
    unpaidStudent = []
    # print(paidStudent, className)

    for ss_foc in focStudent:
        try:
            totalStudent.remove(ss_foc)
        except:
            pass

    for student in totalStudent:
        try:
            if student not in paidStudent:
                unpaidStudent.append(student)
        except:
            pass

    overDueData[className] = unpaidStudent

# print(focStudentData)
for className in studentData:
    try:
        invoiceReport = [len(overDueData.get(className)), len(invoiceData.get(className)), len(focStudentData.get(className))]
        invoiceReportLabel = ['\n'.join(overDueData.get(className)), '\n'.join(invoiceData.get(className)), '\n'.join(focStudentData.get(className))]
    except:
        pass
    invoiceReportLegendLabel = ['Unpaid', 'Paid', 'FOC']
    pieColor = ['red', 'green', 'blue']

    fig1, ax1 = plt.subplots()
    ax1.pie(invoiceReport, labels=invoiceReportLabel, autopct='%1.1f%%', startangle=270, colors = pieColor)
    ax1.legend(labels=invoiceReportLegendLabel, title=className, bbox_to_anchor=(1,0), loc="lower right", bbox_transform=plt.gcf().transFigure)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

