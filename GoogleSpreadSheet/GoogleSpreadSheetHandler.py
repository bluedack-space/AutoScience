
# Ref https://www.twilio.com/blog/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python-jp

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope  =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds  = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("AutoScience").sheet1

# Extract and print all of the values
list_of_hashes = sheet.get_all_records()
print(list_of_hashes)

# Inserting Row Data
row   = ["I'm","inserting","a","row","into","a,","Spreadsheet","with","Python"]
index = 10
sheet.insert_row(row, index)

# Inserting Cell Data
sheet.update_cell(11, 1, "I just wrote to a spreadsheet using Python!")
