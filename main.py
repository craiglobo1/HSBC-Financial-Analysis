from sys import argv
import pandas
import re
from datetime import datetime
import os

def normalize_sheet(sheet : pandas.DataFrame):
    deleted = []
    days    = []
    months  = []
    years   = []
    for i, row in enumerate(sheet["Organization"]):
        # sheet.at[i,"Organization"] = re.sub("(?i)(edmonton)", "", sheet["Organization"][i])
        # sheet.at[i,"Organization"] = re.sub("\s(?i)(ab)", "", sheet["Organization"][i])

        sheet.at[i,"Organization"] = sheet.at[i,"Organization"].rsplit(maxsplit=2)[0]
        sheet.at[i,"Organization"] = re.sub("[^a-zA-Z\s:]", "", sheet["Organization"][i])
        sheet.at[i,"Organization"] = sheet.at[i,"Organization"].upper()
        sheet.at[i,"Organization"] = sheet.at[i,"Organization"].strip()

        date = datetime.strptime(sheet.at[i,"date added"],"%Y-%m-%d")

        days.append(date.day)
        months.append(date.strftime("%b"))
        years.append(date.year)
        

        if sheet.at[i, "Amount"] > 0:
            deleted.append(i)

        sheet.at[i,"Amount"] = abs(sheet.at[i,"Amount"])

    sheet.insert(1,"Day", days, True)
    sheet.insert(1,"Year", years, True)
    sheet.insert(1,"Month", months, True)

    sheet = sheet.drop(sheet.index[deleted])
    sheet = sheet.drop("date added", axis=1)

    sheet["Category"] = "None"
    return sheet

def generate_md_file(sheet : pandas.DataFrame, total_cost):
    table_md = sheet.to_markdown()

    md_text = "# Financial Sheet\n"
    md_text += table_md
    md_text += f"\n\n> **total_cost:** {total_cost:.2f}"
    with open("files/transactions.md", "w+") as wf:
        wf.write(md_text)


def main():

    if len(argv) <= 1:
        print("Error: filename not given")
        return
    argv.reverse()
    argv.pop()
    csv_name = argv.pop()

    sheet = pandas.read_csv(csv_name,usecols=[0,2,3], names=["date added","Organization", "Amount"])
    sheet = normalize_sheet(sheet)

    while len(argv) > 0:
        match argv.pop():
            case "-m":
                month = argv.pop()
                sheet = sheet[sheet["Month"] == month]
            case _:
                print("Error: invalid flag given, check -h for help")
                return

    


    total_cost = sheet["Amount"].sum()

    generate_md_file(sheet, total_cost)
    os.system("md2pdf files/transactions.md")


main()