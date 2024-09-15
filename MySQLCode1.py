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
    '''
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



