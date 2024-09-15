import warnings
warnings.filterwarnings('ignore', category=ImportWarning, module='_bootstrap.py')

import time
import glob
import os
import shutil
import re


import pandas as pd
import numpy
import numpy as np
import openpyxl

from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import timedelta
from datetime import datetime
from datetime import date
from time import gmtime, strftime

import urllib
from sqlalchemy import create_engine

from urllib.parse import quote 

#import MySQLdb


import pymysql
import pymysql.cursors

import string


def ProcessFile():

    start_time = time.time()

    print(datetime.now())
    

    #list_of_files = glob.glob("D:\\CID\\CID*.xlsx")
    list_of_files = glob.glob("CID*.xlsx")
    if len(list_of_files) > 0:
        latest_file = max(list_of_files,key = os.path.getctime)
    else:
        print("No file found with CID name in .xlsx format"); time.sleep(3); quit()
    
    print("Processing CID Sheet...." + latest_file)
    
    CIDFile = latest_file

    dfCID = pd.read_excel(CIDFile, sheet_name = "LTE", usecols = "F,G,J,V,Y,Z,AC") 

    dfCID.rename(columns={"2G/3G/4G Status":"Site","ECI Received (Hex)":"ECGI","Address":"Location","Orientation":"Ornt"},inplace= True)

    dfCID.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    dfCID.columns = dfCID.columns.str.strip()

    dfCID['Lat'].fillna(0, inplace = True)
    dfCID['Long'].fillna(0, inplace = True)

    dfCID["Location"].str.encode('ascii', 'ignore').str.decode('ascii')
    dfCID.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)
    dfCID["Location"] = dfCID["Location"].str.strip()

    #dfCID["Ornt"].replace("-",'0',inplace = True)
    #dfCID["Ornt"].replace("COW",'0',inplace = True)

    dfCID['Ornt'] = dfCID['Ornt'].astype(str)
    #dfCID.loc[(dfCID["Ornt"].str.contains("Indoor",na = False,case= False)), "Ornt"] = "0"
    #dfCID.loc[(dfCID["Ornt"].str.contains("IBS",na = False,case= False)), "Ornt"] = "0"
    dfCID.loc[(dfCID["Ornt"].isnull()) | (dfCID["Ornt"] == '') |(dfCID["Ornt"] == '-') | (dfCID["Ornt"] == 'COW')| (dfCID["Ornt"] == 'IBS') | (dfCID["Ornt"] == 'Indoor'),"Ornt"] = "0"

    dfCID['Lat'] = dfCID['Lat'].astype(str)
    dfCID['Long'] = dfCID['Long'].astype(str)
    dfCID.loc[(dfCID["Lat"].isnull()) | (dfCID["Lat"] == ''),"Lat"] = "0"
    dfCID.loc[(dfCID["Long"].isnull()) | (dfCID["Long"] == ''),"Long"] = "0"
    dfCID.loc[(dfCID["Lat"] == " "),"Lat"] = "0"
    dfCID.loc[(dfCID["Long"] == " "),"Long"] = "0"
    dfCID.loc[(dfCID["Lat"].str.contains("COW",na = False,case= False)), "Lat"] = "0"
    dfCID.loc[(dfCID["Long"].str.contains("COW",na = False,case= False)), "Long"] = "0"
    
    dfCID.loc[(dfCID["City"].isnull()) | (dfCID["City"] == ''),"City"] = "-"

    dfCID["Location"].replace("\t",'-',inplace = True)
    dfCID["Location"].replace("\r",'-',inplace = True)
    dfCID['Location'] = dfCID['Location'].str.replace(r"[\"\',]", '-')
    dfCID.loc[(dfCID["Location"].isnull()) | (dfCID["Location"] == ''),"Location"] = "-"
    dfCID.loc[(dfCID["Location"] == '#N/A') | (dfCID["Location"] == 'N/A'),"Location"] = "-"
    dfCID.loc[(dfCID["Location"].apply(str).map(len) > 200),"Location"] = dfCID["Location"].str[1:200]

    dfCID['Location'].replace(regex=True,inplace=True,to_replace=r'¿',value=r'')

    dfCID['Location'].replace(regex=True,inplace=True,to_replace=r'┬┐',value=r'')
    

    
    dfCID = dfCID.fillna(0)
    


    spec_chars = ["╖","┬","Ñ","á","┬╖","`","'","{","|","}","~","3⁄4"]
    for char in spec_chars:
        dfCID['Location'] = dfCID['Location'].str.replace(char, ' ')

    dfCID['Lat'].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')
    dfCID['Long'].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')

    dfCID["Lat"] = dfCID["Lat"].replace('nan', np.nan).fillna(0)
    dfCID["Long"] = dfCID["Long"].replace('nan', np.nan).fillna(0)
    dfCID["Ornt"] = dfCID["Ornt"].replace('nan', np.nan).fillna(0)

    dfCID["Lat"] = dfCID["Lat"].replace('', '0')
    dfCID["Long"] = dfCID["Long"].replace('', '0')
    dfCID["Ornt"] = dfCID["Ornt"].replace('', '0')


    dfCID["Ornt"]= pd.to_numeric(dfCID["Ornt"], errors='coerce').fillna(0).astype(np.int64)

    dfCID.fillna(0)

    #print (dfCID.dtypes)
    #print (dfCID.shape)

    dfCID["Lat"]= pd.to_numeric(dfCID["Lat"], errors='coerce').fillna(0).astype(np.float64)
    dfCID["Lat"] = dfCID["Lat"].round(4)
    dfCID["Long"]= pd.to_numeric(dfCID["Long"], errors='coerce').fillna(0).astype(np.float64)
    dfCID["Long"] = dfCID["Long"].round(4)
    
    dfCID.to_csv("CIDMySQL.txt", sep = '\t', encoding = 'utf-8',index=False)

    print("Output file generated successfully...")
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    #print("Time taken--- %s seconds ---" % (time.time() - start_time))
    print("Time taken--- %s minutes ---" % round((time.time() - start_time)/60))

def SQLInsert():

    print("Reading processed file...")
    df = pd.read_csv("CIDMySQL.txt",sep = '\t', encoding = 'utf-8', low_memory=False)


    # Step 2: Create a SQLAlchemy engine to connect to the MySQL database
    db_data = 'mysql+pymysql://' + 'root' + ':' + quote('MecGlo@1619') + '@' + 'localhost' + ':3306/' \
       + 'lbs' + '?charset=utf8mb4'
    
    #engine = create_engine('mysql+pymysql://root:%s@localhost:3306/database' % quote('MecGlo@1619'))
    engine = create_engine(db_data)

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                            user='root',
                            password='MecGlo@1619',
                            db='lbs')    

    '''
    # create cursor
    cursor=connection.cursor()
    # Execute the to_sql for writting DF into SQL
    try:
        df.to_sql('cid_tbl', engine, if_exists='replace', index=False)    
    except Exception as e:
        print(e) ;print("CID Sheet update failed")  ;quit()
    
    engine.dispose()
    connection.close()
    '''
    
    '''
    #insert into DB
    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                INSERT INTO cid_tbl (Site, Location) 
                VALUES ('3G', 'Buffalo Site')
                """)
                connection.commit()
            except pymysql.Error as e:
                print(f"An error occurred: {e.args[0]}, {e.args[1]}")
    finally:
        connection.close()      
    '''
    
    #update DB
    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                UPDATE  cid_tbl
                Set Location = 'COW Site' 
                where Location = 'Buffalo Site'
                """)
                connection.commit()
            except pymysql.Error as e:
                print(f"An error occurred: {e.args[0]}, {e.args[1]}")
    finally:
        connection.close()      

    print("CID Sheet successfully updated")
    os.system('pause')
    

def CreateTable1():

     # Connect to the database
    connection = pymysql.connect(host='localhost',
                            user='root',
                            password='MecGlo@1619',
                            db='lbs')    

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE 'lbs'.'tran_tbl' (
            'ID' int NOT NULL AUTO_INCREMENT,
            'subscriber' varchar(16) NOT NULL,
            'msisdn' varchar(16) NOT NULL,
            'email' varchar(255) DEFAULT NULL,
            'sessionid1' varchar(255) DEFAULT NULL,
            'create_time' timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            'imsi' varchar(20) DEFAULT NULL,
            'sessionid2' varchar(255) DEFAULT NULL,
            'age' varchar(45) DEFAULT NULL,
            'ecgi' varchar(255) DEFAULT NULL,
            'update_time' timestamp NULL DEFAULT NULL,
            'status' int(10) unsigned zerofill DEFAULT NULL,
            PRIMARY KEY ('ID')
            ) ;
            """)
        connection.commit()
    finally:
        connection.close()

def CreateTable2():

     # Connect to the database
    connection = pymysql.connect(host='localhost',
                            user='root',
                            password='MecGlo@1619',
                            db='lbs')    

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE 'lbs'.'cid_tbl' (
            'Site' VARCHAR(12) NULL,
            'Location' VARCHAR(255) NULL,
            'City' VARCHAR(255) NULL,
            'ECGI' VARCHAR(45) NOT NULL,
            'Lat' VARCHAR(45) NULL,
            'Long' VARCHAR(45) NULL,
            'Ornt' VARCHAR(12) NULL
            );

            """)
        connection.commit()
    finally:
        connection.close()


def program_expired():
    app_date = datetime(year=2024,month=8,day=30) #setup a datetime object
    now = datetime.now()
    if (now-app_date).days >=0: #change to 30
        print("Tool expired...");time.sleep(3);quit()
    
def main():
    #program_expired()
    #ProcessFile()
    #SQLInsert()
    CreateTable1()
    #CreateTable2()

if __name__ == "__main__":
    main()



