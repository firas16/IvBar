from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)
import pandas as pd
import numpy as np
import datetime

date_shift = 0

#une autre façon de faire
def convert_mois(month):
    return {
        'JAN': '01',
        'FEB': '02',
        'MAR': '03',
        'APR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AUG': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DEC': '12',
    }[month]

#convert  ENT_MOD,  ENT_PRV to admiisionFrom and DischargeTo
def convert_ENT_MOD(mode):
    return {
        0: 'foclin',
        7: 'focf',
        6: 'foclin',
        8: "fhome",
    }[mode]

def convert_SOR_MOD(mode):
    return {
        0: 'toclin',
        7: 'tocf',
        6: 'toclin',
        8: 'thome',
        9: 'dec'
    }[mode]

## Conversion of gender from numbers to letters
def convert_gender(gender):
    if gender == 1:
        return 'm'
    elif gender == 2:
        return 'f'

# adds subelement to element with name column_name and text value 
def add_value_toTree(column_name, element, value):
    columnSubElement = SubElement(element, column_name)
    columnSubElement.text = value
    return columnSubElement

def add_element_toTree(column_name, element):
    columnSubElement = SubElement(element, column_name)
    return columnSubElement

#PMSI utilities
def fill_das_PMSI(ligne, elementToFill):
    diagnosis = Element('diagnosis')
    ## Creation of the diagnosis' subelements
    typeOfDiagnosis = SubElement(diagnosis, 'typeOfDiagnosis')
    typeOfDiagnosis.text = 'secondary'
    diagnosisTime = SubElement(diagnosis, 'diagnosisTime')
    diagnosisTime.text = 'na'
    diagnosisCode = SubElement(diagnosis, 'diagnosisCode')
    ## Creation of the diagnosisCode's subelements
    code = SubElement(diagnosisCode, 'code')
    code.text = '%s'%ligne.ASS_DGN
    codeSystem = SubElement(diagnosisCode, 'codeSystem')
    codeSystem.text = 'icd10'
    elementToFill.append(diagnosis)


def find_value_PMSI(v, row):
    if (v == ""):
        return ""
    elif (v == "['AN', 'ETA_NUM', 'RSA_NUM']"):
        return "-".join([str(row.name[0]), row.name[1], str(row.name[2])])
    elif (v == "GRG_GHM[5]"):
        return '%s-' % (row.loc["GRG_GHM"][5])
    elif (v == "COD_SEX"):
        return convert_gender(row.loc[v])
    elif (v == "ENT_MOD"):
        return convert_ENT_MOD(row.loc["ENT_MOD"])
    elif (v == "SOR_MOD"):
        return convert_SOR_MOD(row.loc["SOR_MOD"])
    elif (v == "EXE_SOI_DTD"):
        datedebut = datetime.datetime(int(row.loc["EXE_SOI_DTD"][5:9]), int(convert_mois(row.loc["EXE_SOI_DTD"][2:5])),
                                      int(row.loc["EXE_SOI_DTD"][0:2]))
        datedebut_C = datedebut + datetime.timedelta(3)
        return ('%d-%02d-%02d' % (datedebut_C.year, datedebut_C.month, datedebut_C.day))
    elif (v == "EXE_SOI_DTF"):
        datefin = datetime.datetime(int(row.loc["EXE_SOI_DTF"][5:9]), int(convert_mois(row.loc["EXE_SOI_DTF"][2:5])),
                                    int(row.loc["EXE_SOI_DTF"][0:2]))
        datefin_C = datefin + datetime.timedelta(3)
        return ('%d-%02d-%02d' % (datefin_C.year, datefin_C.month, datefin_C.day))
    elif (v == "DT_NAIS"):
        dateNaissance = datetime.datetime.strptime(row.loc["DT_NAIS"].lstrip(), '%Y-%m-%d')
        dateNaissance = dateNaissance + datetime.timedelta(6)
        return ('%d-%02d-%02d' % (dateNaissance.year, dateNaissance.month, dateNaissance.day))
    elif (type(v) == list):
        return v[1]
    elif (v == "ETA_NUM"):
        return row.name[1]
    elif (v == "RSA_NUM"):
        return row.name[2]
    elif (v == "AN"):
        return row.name[0]
    else:
        return '%s' % (row.loc[v])


def tree_generator_PMSI(dict_var, row, source, dat_ent, data_das, data_ccam):
    if (dat_ent == ""):
        dat_ent = '%s' % (row.loc["ENT_DAT"])
    for k, v in dict_var.items():
        if isinstance(v, dict):
            element = add_element_toTree(k, source)
            if (k == "diagnoses"):
                diagnosis = SubElement(element, 'diagnosis')
                ## Creation of the diagnosis' subelements
                typeOfDiagnosis = SubElement(diagnosis, 'typeOfDiagnosis')
                typeOfDiagnosis.text = 'main'
                diagnosisCode = SubElement(diagnosis, 'diagnosisCode')
                ## Creation of the diagnosisCode's subelements
                code = SubElement(diagnosisCode, 'code')
                code.text = '%s' % (row.DGN_PAL)
                codeSystem = SubElement(diagnosisCode, 'codeSystem')
                codeSystem.text = 'icd10'
                # add_element_toTree(diagnosis, element)
                if (pd.isnull(row.DGN_REL) == False):
                    diagnosis = SubElement(element, 'diagnosis')
                    ## Creation of the diagnosis' subelements
                    typeOfDiagnosis = SubElement(diagnosis, 'typeOfDiagnosis')
                    typeOfDiagnosis.text = 'secondary'
                    diagnosisCode = SubElement(diagnosis, 'diagnosisCode')
                    ## Creation of the diagnosisCode's subelements
                    code = SubElement(diagnosisCode, 'code')
                    code.text = '%s' % (row.DGN_REL)
                    codeSystem = SubElement(diagnosisCode, 'codeSystem')
                    codeSystem.text = 'icd10'
                if (row.NBR_DGN != 0):

                    indexRow = (row.name[0], str(row.name[1]), row.name[2])

                    das = data_das.loc[indexRow]
                    das.apply(lambda x: tree_generator_PMSI(v, x, element, dat_ent, data_das, data_ccam), axis=1)
            elif (k == "procedures"):
                indexRow = (row.name[0], str(row.name[1]), row.name[2])
                if(indexRow in data_ccam.index):
                    ccam = data_ccam.loc[indexRow]
                    ccam.apply(lambda x: tree_generator_PMSI(v, x, element, dat_ent, data_das, data_ccam), axis=1)
            else:
                tree_generator_PMSI(v, row, element, dat_ent, data_das, data_ccam)

        else:
            value = find_value_PMSI(v, row)
            if (type(value) != "int"):
                value = (value).lstrip()
            if (v == "ENT_DAT_DEL"):
                if (len(dat_ent) == 7):
                    dat_ent = "0" + dat_ent
                datetime_object = datetime.datetime.strptime(dat_ent, '%d%m%Y')
                if (value != "nan"):
                    value = int(float(value))
                else:
                    value = 0
                date = datetime_object + datetime.timedelta(value + 3)
                value = ('%d-%02d-%02d' % (date.year, date.month, date.day))

            # print(value)
            if (k == "insurance"):
                ColumnSubElement = SubElement(source, k, attrib={'xmlns': 'urn:era:carecontacts:3:cnamts'})
                ColumnSubElement.text = value
                element = ColumnSubElement
            elif (value == "prado"):
                ColumnSubElement = SubElement(source, k, attrib={'xmlns': 'urn:era:carecontacts:3:cnamts'})
                ColumnSubElement.text = value
                element = ColumnSubElement
            else:
                element = add_value_toTree(k, source, value)

# ACE utilities
def find_value_ACE(v, row):
    if(v == ""):
        return ""
    elif (v == "DT_ACE") :
        dateACE = datetime.datetime(int(row.loc["DT_ACE"][5:9]), int(convert_mois(row.loc["DT_ACE"][2:5])), int(row.loc["DT_ACE"][0:2]))
        dateACE_C = dateACE + datetime.timedelta(date_shift)
        return ('%d-%02d-%02d'%(dateACE_C.year, dateACE_C.month, dateACE_C.day))
    elif(v == "EXE_SPE"):
        return '%s'%(int(float(row.loc[v])))
    elif(type(v) == list):
        return v[1]
    else:
        return '%s'%(row.loc[v])

def tree_generator_ACE(dict_var, row, source):
    for k, v in dict_var.items():
        if isinstance(v, dict):
            if(k == "staffTypes"):
                if(pd.isnull(row.EXE_SPE) == False and row.EXE_SPE not in ("GO", "NC")):
                    element = add_element_toTree(k, source)
                    tree_generator_ACE(v, row, element)
            else :
                element = add_element_toTree(k, source)
                tree_generator_ACE(v, row, element)
        else:
            value = find_value_ACE(v, row)
            if(type(value) != "int"):
                value = (value).lstrip()
                
            #print(value)
            element = add_value_toTree(k, source, value)

# DCIR utilities
def find_value_DCIR(v, row):
    if(v == ""):
        return ""
    elif (v == "DT_PRESTA") :
        dateDCIR = datetime.datetime(int(row.loc["DT_PRESTA"][5:9]), int(convert_mois(row.loc["DT_PRESTA"][2:5])), int(row.loc["DT_PRESTA"][0:2]))
        dateDCIR_C = dateDCIR + datetime.timedelta(date_shift)
        return ('%d-%02d-%02d'%(dateDCIR_C.year, dateDCIR_C.month, dateDCIR_C.day))
    elif(type(v) == list):
        return v[1]
    else:
        return '%s'%(row.loc[v])

def tree_generator_DCIR(dict_var, row, source):
    for k, v in dict_var.items():
        if isinstance(v, dict):
            if (k == "staffType1") | (k == "staffType2") :
                element = add_element_toTree("staffType", source)
                tree_generator_DCIR(v, row, element)
            else :
                element = add_element_toTree(k, source)
                tree_generator_DCIR(v, row, element)
        else:
            value = find_value_DCIR(v, row)
            if(type(value) != "int"):
                value = (value).lstrip()
                
            #print(value)
            element = add_value_toTree(k, source, value)