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

def fill_das(ligne, elementToFill):
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

def find_value(v, row):
    if(v == ""):
        return ""
    elif (v == "['AN', 'ETA_NUM_C', 'RSA_NUM_C']"):
        return ('%s-%s-%s'%(row.loc["AN"], row.loc["ETA_NUM_C"], row.loc["RSA_NUM_C"]))
    elif (v == "GRG_GHM[5]"):
        return '%s-'%(row.loc["GRG_GHM"][5])
    elif (v == "COD_SEX"):
        return convert_gender(row.loc[v])
    elif (v == "EXE_SOI_DTD") :
        datedebut = datetime.datetime(int(row.loc["EXE_SOI_DTD"][5:9]), int(convert_mois(row.loc["EXE_SOI_DTD"][2:5])), int(row.loc["EXE_SOI_DTD"][0:2]))
        datedebut_C = datedebut + datetime.timedelta(3)
        return ('%d-%02d-%02d'%(datedebut_C.year, datedebut_C.month, datedebut_C.day))
    elif(v == "EXE_SOI_DTF") :
        datefin = datetime.datetime(int(row.loc["EXE_SOI_DTF"][5:9]), int(convert_mois(row.loc["EXE_SOI_DTF"][2:5])), int(row.loc["EXE_SOI_DTF"][0:2]))
        datefin_C = datefin + datetime.timedelta(3)
        return ('%d-%02d-%02d'%(datefin_C.year, datefin_C.month, datefin_C.day))
    elif(v == "DT_NAIS"):
        dateNaissance = datetime.datetime.strptime(row.loc["DT_NAIS"].lstrip(), '%Y-%m-%d')
        dateNaissance = dateNaissance + datetime.timedelta(6)
        return ('%d-%02d-%02d'%(dateNaissance.year, dateNaissance.month, dateNaissance.day))
    elif(type(v) == list):
        return v[1]
    else:
        return '%s'%(row.loc[v])

def tree_generator(dict_var, row, source, dat_ent):
    if(dat_ent == ""):
        dat_ent = '%s'%(row.loc["ENT_DAT"])
    for k, v in dict_var.items():
        if isinstance(v, dict):
            element = add_element_toTree(k, source)
            if(k == "diagnoses"):
                diagnosis = SubElement(element, 'diagnosis')
                ## Creation of the diagnosis' subelements
                typeOfDiagnosis = SubElement(diagnosis, 'typeOfDiagnosis')
                typeOfDiagnosis.text = 'main'
                diagnosisCode = SubElement(diagnosis, 'diagnosisCode')
                ## Creation of the diagnosisCode's subelements
                code = SubElement(diagnosisCode, 'code')
                code.text = '%s'%(row.DGN_PAL)
                codeSystem = SubElement(diagnosisCode, 'codeSystem')
                codeSystem.text = 'icd10'
                #add_element_toTree(diagnosis, element)
                if(pd.isnull(row.DGN_REL) == False):
                    diagnosis = SubElement(element, 'diagnosis')
                    ## Creation of the diagnosis' subelements
                    typeOfDiagnosis = SubElement(diagnosis, 'typeOfDiagnosis')
                    typeOfDiagnosis.text = 'secondary'
                    diagnosisCode = SubElement(diagnosis, 'diagnosisCode')
                    ## Creation of the diagnosisCode's subelements
                    code = SubElement(diagnosisCode, 'code')
                    code.text = '%s'%(row.DGN_REL)
                    codeSystem = SubElement(diagnosisCode, 'codeSystem')
                    codeSystem.text = 'icd10'
                if(row.NBR_DGN != 0):
                    das = data_das[(data_das.AN == row.AN) & (data_das.ETA_NUM_C == row.ETA_NUM_C) & (data_das.RSA_NUM_C == row.RSA_NUM_C)]
                    das.apply(lambda x: tree_generator(v, x, element, dat_ent), axis = 1 )
            elif (k == "procedures"):
                if row.NBR_ACT != 0:    
                    ccam = data_ccam[(data_ccam.AN == row.AN) & (data_ccam.ETA_NUM_C == row.ETA_NUM_C) & (data_ccam.RSA_NUM_C == row.RSA_NUM_C)]
                    ccam.apply(lambda x: tree_generator(v, x, element, dat_ent), axis = 1 )
            else:
                tree_generator(v, row, element, dat_ent)
            
        else:
            value = find_value(v, row)
            if(type(value) != "int"):
                value = (value).lstrip()
            if(v == "ENT_DAT_DEL"):
                if(len(dat_ent) == 7):
                    dat_ent = "0" + dat_ent
                datetime_object = datetime.datetime.strptime(dat_ent, '%d%m%Y')
                if(value != "nan"):
                    value = int(float(value))
                else:
                    value = 0
                date = datetime_object + datetime.timedelta(value + 3)
                value = ('%d-%02d-%02d'%(date.year, date.month, date.day))
                
            #print(value)
            element = add_value_toTree(k, source, value)
   
    