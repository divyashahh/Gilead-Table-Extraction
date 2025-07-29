import csv

N = 100  # number of rows to display

with open("outputs/Gilead_digital_structured.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for idx, row in enumerate(reader):
        print(row)
        if idx == N - 1:
            break