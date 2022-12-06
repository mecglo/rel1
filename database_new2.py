import sys
from sqlalchemy import Column, Integer, String, MetaData, Table, Boolean, ForeignKey, select, UniqueConstraint, DateTime
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import json
import datetime
#engine = create_engine('sqlite:///sales.db', echo = True)
engine = create_engine('mysql://dbeaver:password@localhost/hss2', echo = True)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Create database if it does not exist.
if not database_exists(engine.url):
    create_database(engine.url)
else:
    # Connect the database if exists.
    engine.connect()

class APN(Base):
    __tablename__ = 'apn'
    apn_id = Column(Integer, primary_key=True)
    apn = Column(String(50), nullable=False)
    pgw_address = Column(String(50))
    sgw_address = Column(String(50))
    charging_characteristics = Column( String(4), default='0800')
    apn_ambr_dl = Column(Integer, nullable=False)
    apn_ambr_ul = Column(Integer, nullable=False)
    qci = Column(Integer, default=9)
    arp_priority = Column(Integer, default=4)
    arp_preemption_capability = Column(Boolean, default=False)
    arp_preemption_vulnerability = Column(Boolean, default=True)

class Serving_APN(Base):
    __tablename__ = 'serving_apn'
    serving_apn_id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey('subscriber.subscriber_id'))
    apn = Column(Integer, ForeignKey('apn.apn_id'))
    serving_pgw = Column(String(50))
    serving_pgw_timestamp = Column(DateTime)


class AUC(Base):
    __tablename__ = 'auc'
    auc_id = Column(Integer, primary_key = True)
    ki = Column(String(32))
    opc = Column(String(32))
    amf = Column(String(4))
    sqn = Column(Integer)


class SUBSCRIBER(Base):
    __tablename__ = 'subscriber'
    subscriber_id = Column(Integer, primary_key = True)
    imsi = Column(String(18), unique=True)
    enabled = Column(Boolean, default=1)
    auc_id = Column(Integer, ForeignKey('auc.auc_id'))
    default_apn = Column(Integer, ForeignKey('apn.apn_id'))
    apn_list = Column(String(18))
    msisdn = Column(String(18))
    ue_ambr_dl = Column(Integer, default=999999)
    ue_ambr_ul = Column(Integer, default=999999)
    nam = Column(Integer, default=0)
    subscribed_rau_tau_timer = Column(Integer, default=300)
    serving_mme = Column(String(50))
    serving_mme_timestamp = Column(DateTime)

class IMS_SUBSCRIBER(Base):
    __tablename__ = 'ims_subscriber'
    ims_subscriber_id = Column(Integer, primary_key = True)
    msisdn = Column(String(18), unique=True)
    msisdn_list = Column(String(1200))
    imsi = Column(String(18), unique=False)
    ifc_path = Column(String(18))
    sh_profile = Column(String(12000))
    scscf = Column(String(50))
    scscf_timestamp = Column(DateTime)


Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()

def GetObj(obj_type, obj_id):
    result = session.query(obj_type).get(obj_id)
    result = result.__dict__
    result.pop('_sa_instance_state')
    return result

def UpdateObj(obj_type, json_data, obj_id):
    print("Called UpdateObj() for type " + str(obj_type) + " id " + str(obj_id) + " with JSON data: " + str(json_data))
    obj_type_str = str(obj_type.__table__.name).upper()
    print("obj_type_str is " + str(obj_type_str))
    filter_input = eval(obj_type_str + "." + obj_type_str.lower() + "_id==obj_id")
    sessionquery = session.query(obj_type).filter(filter_input)
    print("got result: " + str(sessionquery.__dict__))
    sessionquery.update(json_data, synchronize_session = False)
    session.commit()
    return GetObj(obj_type, obj_id)

def DeleteObj(obj_type, obj_id):
    res = session.query(obj_type).get(obj_id)
    session.delete(res)
    session.commit()
    return {"Result":"OK"}

def CreateObj(obj_type, json_data):
    newObj = obj_type(**json_data)
    session.add(newObj)
    session.commit()
    session.refresh(newObj)
    result = newObj.__dict__
    result.pop('_sa_instance_state')
    return result

def Generate_JSON_Model_for_Flask(obj_type):
    from alchemyjsonschema import SchemaFactory
    from alchemyjsonschema import NoForeignKeyWalker
    import pprint as pp
    factory = SchemaFactory(NoForeignKeyWalker)
    dictty = dict(factory(obj_type))
    dictty['properties'] = dict(dictty['properties'])

    #Set the ID Object to not required
    obj_type_str = str(dictty['title']).lower()
    dictty['required'].remove(obj_type_str + '_id')
   
    return dictty

def Get_IMS_Subscriber(imsi):
    return

def Get_Subscriber(imsi):
    try:
        result = session.query(SUBSCRIBER).filter_by(imsi=imsi).one()
    except:
        raise ValueError("Subscriber not Found")
    result = result.__dict__
    result.pop('_sa_instance_state')
    return result

def Get_APN(apn_id):
    try:
        result = session.query(APN).filter_by(apn_id=apn_id).one()
    except:
        raise ValueError("APN not Found")
    result = result.__dict__
    result.pop('_sa_instance_state')
    return result    

def Get_Vectors(imsi):
    return

def Update_AuC(imsi, sqn):
    return

def Update_Serving_MME(imsi, serving_mme):
    result = session.query(SUBSCRIBER).filter_by(imsi=imsi).one()
    if len(serving_mme) != 0:
        result.serving_mme = serving_mme
        result.serving_mme_timestamp = datetime.datetime.now()
    else:
        #Clear values
        result.serving_mme = None
        result.serving_mme_timestamp = None
    session.commit()
    return

def Update_Location(imsi, apn, diameter_realm, diameter_peer, diameter_origin):
    return

def Get_IMSI_from_MSISDN(msisdn):
    return

if __name__ == "__main__":

    import binascii,os
    apn2 = {'apn':'fadsgdsags', \
        'apn_ambr_dl' : 9999, 'apn_ambr_ul' : 9999, \
        'arp_priority': 1, 'arp_preemption_capability' : False, \
        'arp_preemption_vulnerability': True}
    newObj = CreateObj(APN, apn2)
    print(newObj)
    #input("Created new Object")
    print(GetObj(APN, newObj['apn_id']))
    apn_id = newObj['apn_id']
    UpdatedObj = newObj
    UpdatedObj['apn'] = 'UpdatedInUnitTest'
    
    newObj = UpdateObj(APN, UpdatedObj, newObj['apn_id'])
    print(newObj)

    #Create AuC
    auc_json = {
    "ki": binascii.b2a_hex(os.urandom(16)).zfill(16),
    "opc": binascii.b2a_hex(os.urandom(16)).zfill(16),
    "amf": "9000",
    "sqn": 0
    }
    print(auc_json)
    newObj = CreateObj(AUC, auc_json)
    print(newObj)

    #Get AuC
    newObj = GetObj(AUC, newObj['auc_id'])
    auc_id = newObj['auc_id']
    print(newObj)


    #Update AuC
    newObj['sqn'] = newObj['sqn'] + 10
    newObj = UpdateObj(AUC, newObj, auc_id)

    #New Subscriber
    subscriber_json = {
        "imsi": "001001000000003",
        "enabled": True,
        "msisdn": "123456789",
        "ue_ambr_dl": 999999,
        "ue_ambr_ul": 999999,
        "nam": 0,
        "subscribed_rau_tau_timer": 600,
        "auc_id" : auc_id,
        "default_apn" : apn_id,
        "apn_list" : apn_id
    }
    print(subscriber_json)
    newObj = CreateObj(SUBSCRIBER, subscriber_json)
    print(newObj)
    subscriber_id = newObj['subscriber_id']

    #Get SUBSCRIBER
    newObj = GetObj(SUBSCRIBER, subscriber_id)
    print(newObj)

    #Update SUBSCRIBER
    newObj['msisdn'] = '99942131'
    newObj = UpdateObj(SUBSCRIBER, newObj, subscriber_id)


    # #New IMS Subscriber
    # ims_subscriber_json = {
    #     "msisdn": "123456789013", 
    #     "msisdn_list": "1234567890",
    #     "imsi": "123456789",
    #     "ifc_path" : "default_ifc.xml",
    #     "sh_profile" : "default_sh_user_data.xml"
    # }
    # print(ims_subscriber_json)
    # newObj = CreateObj(IMS_SUBSCRIBER, ims_subscriber_json)
    # print(newObj)
    # ims_subscriber_id = newObj['ims_subscriber_id']


    #Test Get Subscriber
    GetSubscriber_Result = Get_Subscriber(subscriber_json['imsi'])
    print(GetSubscriber_Result)

    #Test Update MME Location
    Update_Serving_MME(subscriber_json['imsi'], 'serving_mme.3gppnetwork.org')
    input("Clear MME Location?")
    Update_Serving_MME(subscriber_json['imsi'], '')

    #Test getting APNs
    GetAPN_Result = Get_APN(GetSubscriber_Result['default_apn'])
    print(GetAPN_Result)

    input("Delete?")
    #Delete IMS Subscriber
    #print(DeleteObj(IMS_SUBSCRIBER, ims_subscriber_id))
    #Delete Subscriber
    print(DeleteObj(SUBSCRIBER, subscriber_id))
    #Delete AuC
    print(DeleteObj(AUC, auc_id))
    #Delete APN
    print(DeleteObj(APN, apn_id))