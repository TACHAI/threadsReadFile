# _*_coding:utf-8_*_
import csv

with open("testCase.csv","r",encoding="utf-8")as csvfile:

    #读取csv文件，返回的是迭代类型
    read = csv.reader(csvfile)
    temp = 3
    for index,rows in enumerate(read):
        if index ==temp:
            row = rows
            print(row[0])
            temp +=23
            test = open("test.txt","a",encoding="utf-8")
            test.write("\n"+row[0]+","+row[1])


