import gspread
from oauth2client.service_account import ServiceAccountCredentials

#[01] Login issues
scope  = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds  = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

#[02] Add New Row Data to Cloud File
import numpy as np
y1     = np.random.rand()
y2     = np.random.rand()
sheet  = client.open("AutoScience").sheet1
sheet.append_row([0.1,y1,y2])

#[03] Plot by Cloud File
xList  = []
y1List = []
y2List = []
for i in range(50):
    x  = sheet.cell(i+1,1).value
    y1 = sheet.cell(i+1,2).value
    y2 = sheet.cell(i+1,3).value
    xList.append(x)
    y1List.append(y1)
    y2List.append(y2)

print(xList)
print(y1List)

import plotly.express as px
fig = px.scatter(x=xList, y=y1List)
fig.show()