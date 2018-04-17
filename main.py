import pandas as pd
import numpy as np
import datetime
from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)
import json
from utils.utilities import *
import time

source = "DCIR"  # source is a config parameter that should be equal to DCIR, ACE or PMSI

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
        print("File ",i)
        tree = ElementTree()
        root = Element('eraCareContacts', attrib={'xmlns': 'urn:era:carecontacts:3'})
        tree._setroot(root)
        version = SubElement(root, 'version')
        version.text = '3.0.1'
        ## Creation of the root's subelement named "careContacts"
        careContacts = SubElement(root, 'careContacts')
        begin = i * max_xml_size
        end = min((i + 1) * max_xml_size, len(data_dcir))
        data_dcir[begin:end].apply(lambda x: tree_generator_DCIR(records, x, careContacts), axis=1)
        result_path = "D:/Mehdi/Carecontact/" + source + "/" + "era_care_contact_3_0_fr-cnamts_" + source + str(
            i) + "_p14n.xml"
        tree.write(result_path, encoding='UTF-8', xml_declaration='True')
elif (source == "PMSI"):
    print("PMSI transformation")
    cols = ['AN', 'ETA_NUM', 'RSA_NUM', 'DGN_PAL', 'DGN_REL', 'NBR_DGN', 'NBR_ACT', 'EXE_SOI_DTD', 'EXE_SOI_DTF',
            'NUM_ENQ', 'DT_NAIS', 'COD_SEX', 'ENT_MOD', 'SOR_MOD', 'ENT_DAT']
    data_sejours = pd.read_table(conf["path_sejours"], sep=';', usecols = cols, low_memory=False)
    print("number of occurences: ", len(data_sejours))

    data_das = pd.read_table(conf["path_das"], sep=';')
    data_ccam = pd.read_table(conf["path_ccam"], sep=';')

    # Clean data
    # Filter incorrect Date naissance
    data_sejours = data_sejours.loc[data_sejours["DT_NAIS"] != ".-01-01"]
    #filter bad acts
    print("length ccam : ", len(data_ccam))
    print(data_ccam.dtypes)

    data_ccam = data_ccam[(data_ccam["ACV_ACT"] != 4) & ((data_ccam["PHA_ACT"] == 0) | (data_ccam["PHA_ACT"] == 1))]
    # Filter incorrect code acts and das
    print("new length ccam : ", len(data_ccam))
    # Join tables
    # data_sejour_with_das = pd.merge(data_sejours, data_das, how='left', left_on=['AN', 'ETA_NUM', 'RSA_NUM'],
    #                                 right_on=['AN', 'ETA_NUM', 'RSA_NUM'])
    # data_sejour_with_das_with_ccam = pd.merge(data_sejour_with_das, data_ccam, how='left',
    #                                 left_on=['AN', 'ETA_NUM', 'RSA_NUM'], right_on=['AN', 'ETA_NUM', 'RSA_NUM'])


    #add indexes
    data_sejours.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)
    data_das.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)
    data_ccam.set_index(['AN', 'ETA_NUM', 'RSA_NUM'], inplace=True)

    data_sejours.sort_index(inplace=True)
    data_das.sort_index(inplace=True)
    data_ccam.sort_index(inplace=True)
    # data_sejours = data_sejours.reindex(natsorted(data_sejours.index))
    # data_das = data_das.reindex(natsorted(data_das.index))
    # data_ccam = data_ccam.reindex(natsorted(data_ccam.index))


    size_df = len(data_sejours.index) // max_xml_size
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
        end = min((i + 1) * max_xml_size, len(data_sejours))
        result_path = "D:/Mehdi/Carecontact/" + source + "2/" + "era_care_contact_3_0_fr-cnamts_" + source + str(i) + "_p14n.xml"
        #data_sejours.groupBy(['AN', 'ETA_NUM', 'RSA_NUM'])['']

        data_sejours[begin:end].apply(lambda x: tree_generator_PMSI(records, x, careContacts, "", data_das, data_ccam), axis=1)
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
        result_path = "D:/Mehdi/Carecontact/"+ source + "/" + "era_care_contact_3_0_fr-cnamts_" + source + str(i) +"_p14n.xml"
        tree.write(result_path, encoding='UTF-8', xml_declaration='True')

elapsed_time = time.time() - start_time
print("elapsed_time ", elapsed_time)