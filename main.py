import pandas as pd
import numpy as np
import datetime
from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)
import json
from utils.utilities import *
import time

source = "ACE"  # source is a config parameter that should be equal to DCIR, ACE or PMSI

# read conf
with open("appConf.json") as content_file:
    content = content_file.read()
conf = json.loads(content)

start_time = time.time()

# read schema CNAM <=> IvBar correspondance
with open("source/" + source + "/schema.json") as content_file:
    content = content_file.read()
records = json.loads(content)

tree = ElementTree()
root = Element('eraCareContacts', attrib={'xmlns': 'urn:era:carecontacts:3'})

## Creation of the root's subelement named "version"
version = SubElement(root, 'version')
version.text = '3.0.1'

max_xml_size = 200000

if (source == "DCIR"):
    data_dcir = pd.read_table(conf["path_dcir"], sep=';', dtype=conf["columns_types_dcir"])
    data_dcir["careContactId"] = pd.Series(np.arange(len(data_dcir.index)))
    size_df = len(data_dcir.index) // max_xml_size
    for i in range(0, size_df + 1):
        # Build XML
        tree = ElementTree()
        root = Element('eraCareContacts', attrib={'xmlns': 'urn:era:carecontacts:3'})
        tree._setroot(root)
        ## Creation of the root's subelement named "careContacts"
        careContacts = SubElement(root, 'careContacts')
        begin = i * max_xml_size
        end = min((i + 1) * max_xml_size, len(data_dcir))
        data_dcir[begin:end].apply(lambda x: tree_generator_DCIR(records, x, careContacts), axis=1)
        result_path = str(i) + "_" + conf["output_path"]
        tree.write(result_path, encoding='UTF-8', xml_declaration='True')
elif (source == "PMSI"):
    print("PMSI transformation")
    data_sejours = pd.read_table(conf["path_sejours"], sep=';', dtype=conf["columns_types_sej"])

    #clean data
    data_sejours = data_sejours.loc[data_sejours["DT_NAIS"] != ".-01-01"]

    data_das = pd.read_table(conf["path_das"], sep=';')
    data_ccam = pd.read_table(conf["path_ccam"], sep=';')

    #add indexes
    data_sejours.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)
    data_das.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)
    data_ccam.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)

    size_df = len(data_sejours.index) // max_xml_size
    for i in range(0, size_df + 1):
        print("File ", i)
        tree = ElementTree()
        root = Element('eraCareContacts', attrib={'xmlns': 'urn:era:carecontacts:3'})
        tree._setroot(root)
        ## Creation of the root's subelement named "careContacts"
        careContacts = SubElement(root, 'careContacts')
        begin = i * max_xml_size
        end = min((i + 1) * max_xml_size, len(data_sejours))
        result_path = str(i) + "_" + conf["output_path"]
        data_sejours[begin:end].apply(lambda x: tree_generator_PMSI(records, x, careContacts, "", data_das, data_ccam),
                                      axis=1)
        tree.write(result_path, encoding='UTF-8', xml_declaration='True')
elif (source == "ACE"):
    data_ace = pd.read_table(conf["path_ace"], sep=';', dtype=conf["columns_types_ace"])
    # delete row where date DT_ACE is missing
    data_ace = data_ace.drop(data_ace.index[9578888])

    data_ace = data_ace[pd.to_numeric(data_ace.EXE_SPE, errors='coerce').notnull()]
    data_ace["careContactId"] = pd.Series(np.arange(len(data_ace.index)))
    size_df = len(data_ace.index) // max_xml_size
    for i in range(0, size_df + 1):
        print("File ", i)
        tree = ElementTree()
        root = Element('eraCareContacts', attrib={'xmlns': 'urn:era:carecontacts:3'})
        tree._setroot(root)
        version = SubElement(root, 'version')
        version.text = '3.0.1'
        ## Creation of the root's subelement named "careContacts"
        careContacts = SubElement(root, 'careContacts')
        begin = i * max_xml_size
        end = min((i + 1) * max_xml_size, len(data_ace))
        data_ace[begin:end].apply(lambda x: tree_generator_ACE(records, x, careContacts), axis=1)
        result_path = "target/ACE/" + str(i) + "_" + conf["output_path"]
        tree.write(result_path, encoding='UTF-8', xml_declaration='True')

elapsed_time = time.time() - start_time
print("elapsed_time ", elapsed_time)