import pandas as pd
import numpy as np
import datetime
from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)
import json
from .utilities import *
#%load D:/firas/IvBar/utilities.py

rootPath = "D:/firas/IvBar/"

#read conf
with open(rootPath + "appConf.json") as content_file:
    content = content_file.read()
conf = json.loads(content)

data_sejours = pd.read_table(conf["path_sejours"], sep = ';', dtype = conf["columns_types_sej"]).head(5)
data_das = pd.read_table(conf["path_das"], sep = ';')
data_ccam = pd.read_table(conf["path_ccam"], sep = ';')

#read schema CNAM <=> IvBar correspondance
with open(conf["path_schema"]) as content_file:
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
data_sejours.apply(lambda x: tree_generator(records, x, careContacts, ""), axis = 1 )

#Save XML
tree.write(conf["output_path"], encoding = 'UTF-8', xml_declaration = 'True')