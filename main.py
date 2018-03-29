import pandas as pd
import numpy as np
import datetime
from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)
import json
from utils.utilities import *


rootPath = "D:/firas/IvBar/code/new/IvBar/"
source = "PMSI" #source is a config parameter that should be equal to DCIR, ACE or DCIR

#read conf
with open(rootPath + "appConf.json") as content_file:
    content = content_file.read()
conf = json.loads(content)



#read schema CNAM <=> IvBar correspondance
with open(rootPath + "source/" + source + "/schema.json") as content_file:
    content = content_file.read()
records = json.loads(content)

#Build XML
tree = ElementTree()
root = Element('eraCareContacts', attrib = {'xmlns' : 'urn:era:carecontacts:3'})
tree._setroot(root)

## Creation of the root's subelement named "version"
version = SubElement(root, 'version')
version.text = '3.0.1'

## Creation of the root's subelement named "careContacts"
careContacts = SubElement(root, 'careContacts')
if(source == "DCIR"):
	data_dcir = pd.read_table(conf["path_dcir"], sep = ';', dtype = conf["columns_types_dcir"])
	data_dcir["careContactId"] = pd.Series(np.arange(len(data_dcir.index)))
	data_dcir.apply(lambda x: tree_generator_DCIR(records, x, careContacts), axis = 1 )
elif (source == "PMSI"):
	data_sejours = pd.read_table(conf["path_sejours"], sep = ';', dtype = conf["columns_types_sej"]).head(5)
	data_das = pd.read_table(conf["path_das"], sep = ';')
	data_ccam = pd.read_table(conf["path_ccam"], sep = ';')
	data_sejours.apply(lambda x: tree_generator_PMSI(records, x, careContacts, "", data_das, data_ccam), axis = 1 )
elif (source == "ACE"):
	data_ace = pd.read_table(conf["path_ace"], sep = ';', dtype = conf["columns_types_ace"])
	data_ace["careContactId"] = pd.Series(np.arange(len(data_ace.index)))
	data_ace.apply(lambda x: tree_generator_ACE(records, x, careContacts), axis = 1 )

#Save XML
tree.write(conf["output_path"], encoding = 'UTF-8', xml_declaration = 'True')