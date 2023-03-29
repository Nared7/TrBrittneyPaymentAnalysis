import streamlit as st
import openpyxl as xl
import matplotlib.pyplot as plt
from string import capwords
import json
import gspread
import pandas as pd

# studentDataWB = xl.load_workbook(r'D:\Python_Projects\TrBrittneyInvoice\studentCost.xlsx')
# invoiceDataWB = xl.load_workbook(r'D:\Python_Projects\TrBrittneyInvoice\InvoiceList_Jan2023.xlsx')

# cred_file = r"pages/"
cred_file = r"trbrittneystudentdata-bb3d38df148f.json"
gc = gspread.service_account(filename=cred_file)
database = gc.open('studentData')
invoiceData = gc.open('InvoiceList_March2023')

# info_data = 'Load Data from local Database'
info_data = st.info('Load Data from local Database')
with open('studentData.json') as json_file:
    allStData = json.load(json_file)

with open('invoiceData.json') as json_file:
    invoice_data = json.load(json_file)

studentData = {}
invoiceData = {}
overDueData = {}
focStudentData = {}

dbStudentList = []
inStudentList = []
focStudentList = []
i = 0

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

    for ss_foc in focStudent:
        try:
            totalStudent.remove(ss_foc)
        except:
            pass

    for student in totalStudent:
        if student not in paidStudent:
            unpaidStudent.append(student)

    overDueData[className] = unpaidStudent

print(focStudentData)
for className in studentData:
    invoiceReport = [len(overDueData.get(className)), len(invoiceData.get(className)), len(focStudentData.get(className))]
    invoiceReportLabel = ['\n'.join(overDueData.get(className)), '\n'.join(invoiceData.get(className)), '\n'.join(focStudentData.get(className))]
    invoiceReportLegendLabel = ['Unpaid', 'Paid', 'FOC']
    pieColor = ['red', 'green', 'blue']

    fig1, ax1 = plt.subplots()
    ax1.pie(invoiceReport, labels=invoiceReportLabel, autopct='%1.1f%%', startangle=270, colors = pieColor)
    ax1.legend(labels=invoiceReportLegendLabel, title=className, bbox_to_anchor=(1,0), loc="lower right", bbox_transform=plt.gcf().transFigure)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

