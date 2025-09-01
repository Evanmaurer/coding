import csv
import pandas as pd
import gspread
import time

SUBSCRIPTION_NAMES = {"RECURRING DEBIT PURCHASE PAYPAL *DISCORD 402-935-7733CA" , "RECURRING DEBIT PURCHASE Spotify USA     877-7781161 NY", }
transactions = [
]
def fin(file, SUBSCRIPTION_NAMES):
    transactions = []
    with open(file, mode='r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        for row in csvreader:
            Date = row[0]
            Name = row[2]
            Category = 'other'
            Amount = float(row[4])
            if Name in SUBSCRIPTION_NAMES:
                Category = "Subscription"
            if Name == "DEBIT PURCHASE -VISA MO S&T HAVENER C573-341-4993MO":
                Category = "School food"
            if Name == "ELECTRONIC WITHDRAWAL GAMER2GAMER GLOB":
                Category = "RMT"
            if Name == "DEBIT PURCHASE -VISA PULQUE MEXICAN RWASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA MCDONALD'S F1220UNION       MO" or Name == "DEBIT PURCHASE -VISA MCDONALD'S F4212WASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA TACO BELL 027912ROLLA       MO" or Name == "DEBIT PURCHASE -VISA STEAK-N-SHAKE#06WASHINGTON  MO"or Name == "DEBIT PURCHASE -VISA TACO BELL 4241  WASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA DAIRY QUEEN #418WASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA Subway 56625    Washington  MO" or Name == "DEBIT PURCHASE -VISA TACO LOCO       WASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA APPLEBEES 8119  WASHINGTON  MO" or Name == "DEBIT PURCHASE -VISA STARBUCKS STORE WASHINGTON  MO":
                Category = "Food"
            if Name == "ELECTRONIC WITHDRAWAL LILITH NETWORK H":
                Category = "Gaming"
            if Name == "DEBIT PURCHASE WM SUPERC Wal-MaWASHINGTON  MO":
                Category = "Groceries"
            if Name == "ELECTRONIC DEPOSIT LOWE'S HOME CENT":
                Category = "Salary"
            if Name == "MOBILE BANKING TRANSFER DEPOSIT 9767":
                Category = "Salary"
            transation = (Date, Name, Amount, Category)
            transactions.append(transation)
    return transactions
    
    
#fin(file, SUBSCRIPTION_NAMES)

'''
sa = gspread.service_account()
sh = sa.open("Personal Finances")

wks = sh.worksheet(f"{month}")               
rows = fin(file, SUBSCRIPTION_NAMES)    
for row in rows:
    wks.insert_row((str(row[0]),str(row[1]),str(row[3]), row[2]),8)
    time.sleep(2)
'''