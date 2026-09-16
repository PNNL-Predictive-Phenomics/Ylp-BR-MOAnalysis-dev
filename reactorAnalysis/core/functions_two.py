import numpy as np
import pandas as pd
import glob
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime, time
import warnings
import os
import zipfile
from tempfile import NamedTemporaryFile
warnings.filterwarnings("ignore")

def fix_xlsx_empty_styles(path):
    """
    Deal with invalid empty Fill
    The error looks like this:
    ```
    TypeError: Fill() takes no arguments
    ... stack trace ...
    TypeError: expected <class 'openpyxl.styles.fills.Fill'>
    ```
    """
    with NamedTemporaryFile(delete=False) as tmp:
        zin = zipfile.ZipFile(path, "r")
        zout = zipfile.ZipFile(tmp.name, "w")
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if item.filename == "xl/styles.xml":
                styles = buffer.decode("utf-8")
                styles = styles.replace("<x:fill />", "")
                buffer = styles.encode("utf-8")
            zout.writestr(item, buffer)
        zout.close()
        zin.close()
        # Create a backup of the original file
        backup_path = path + '.bak'
        os.rename(path, backup_path)
        # Replace the original with the fixed file
        os.rename(tmp.name, path)
        print(f"Fixed styles in {path} and backed up original to {backup_path}")

# updated function 10/06/25 to automatically skiprows. 
def read_excel_after_fix(file_path, sheet_name=None):
    fix_xlsx_empty_styles(file_path)  # Fix the styles first
    
    try:
        # Step 1: Temporarily read the first few rows to identify the "Date" row
        preview_df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=None)
        # Find the index of the row containing "Date" in the first column
        skiprows = preview_df.loc[preview_df.iloc[:, 0] == 'Date'].index[0] if 'Date' in preview_df.iloc[:, 0].values else 0

        # Step 2: Read the file skipping rows before the "Date" row (to use "Date" as the header row)
        if sheet_name:
            df = pd.read_excel(file_path, skiprows=skiprows, sheet_name=sheet_name, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, skiprows=skiprows, engine='openpyxl')
        
        return df
    except Exception as e:
        print(f"Error reading {file_path} after fixing styles: {e}")
        return None

# def read_excel_after_fix(file_path, skiprows=0, sheet_name=None):
#     fix_xlsx_empty_styles(file_path)  # Fix the styles first
#     try:
#         if sheet_name:
#             df = pd.read_excel(file_path, skiprows=skiprows, sheet_name=sheet_name, engine='openpyxl')
#         else:
#             df = pd.read_excel(file_path, skiprows=skiprows, engine='openpyxl')
#         return df
#     except Exception as e:
#         print(f"Error reading {file_path} after fixing styles: {e}")
#         return None


def convert_to_hours(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h + m / 60 + s / 3600
    
def merge_dfs(bv,AF1,AF2,AF3):
    '''
    time resolution is not as high for the process data (compared to the blueVis offgas data).
    this function takes the offgas data and the airflow rate for the bioreactor and fills in the time resolved 
    values.
    
    process value records a change. the times with no records indicate that the value (flow rate has stayed the same).
    
    bv: pd.DataFrame(blueVisData [offgas]).
    AF: pd.DataFrame(airflow rate data).
    
    returns:
        combinedDataFrame.
    
    
    '''

#     bv_copy = bv.copy()

    # Updated 11/04/2024 JJC due to errors with Biostat2L_22 processing. 
    # set the indeces to 'age'. 
    # bv = bv.set_index('age')
    # temp = AF1.set_index('age')

    # Ensure that the 'bv' and 'AF1' DataFrames are sorted by their index
    # Updated 02/10/2025 JJC due to errors with merging.
    bv['temp_age_continue']=bv['age']
    bv = bv.set_index('age').sort_index()
    temp = AF1.set_index('age').sort_index()


    # merge the two dataframes, and fill the values in 'backwards'
    merged_df = pd.merge_asof(
        #bv,     # Selecting only the 'age' column from blueVisData_use
        # Updated 02/10/2025 JJC due to errors with merging.
        bv['temp_age_continue'], 
        temp[['value']],  # Selecting the desired column from airflow_in_BDCU2
        left_index=True, right_index=True, direction='backward'
    ).set_index(bv.index)  # Setting the index to match blueVisData_use

    # assign the value to the correct format. 
    bv[('Fermenter01','BDCU-1','F_in1','LPM')]=merged_df.value
    
    
    
    # if two sets of data are maintained in one offgas data. 
    if AF2 is not None:
        temp = AF2.set_index('age')

        merged_df = pd.merge_asof(
            #bv,     # Selecting only the 'age' column from blueVisData_use
            # Updated 02/10/2025 JJC due to errors with merging.
            bv['temp_age_continue'], 
            temp[['value']],  # Selecting the desired column from airflow_in_BDCU2
            left_index=True, right_index=True, direction='backward'
        ).set_index(bv.index)  # Setting the index to match blueVisData_use

        bv[('Fermenter02','BDCU-2','F_in2','LPM')]=merged_df.value

    if AF3 is not None:
        temp = AF3.set_index('age')

        merged_df = pd.merge_asof(
            #bv,     # Selecting only the 'age' column from blueVisData_use
            # Updated 02/10/2025 JJC due to errors with merging.
            bv['temp_age_continue'], 
            temp[['value']],  # Selecting the desired column from airflow_in_BDCU2
            left_index=True, right_index=True, direction='backward'
        ).set_index(bv.index)  # Setting the index to match blueVisData_use

        bv[('Fermenter03','BDCU-3','F_in3','LPM')]=merged_df.value


    
    return bv

def calc_offgas(bv, AF2, AF3, co2_in_cal1=False,o2_in_cal1=False,co2_in_cal2=False,o2_in_cal2=False,co2_in_cal3=False,o2_in_cal3=False):

    if AF3 is not None:
        if not co2_in_cal3:
            co2_in_cal3 = bv[('Fermenter03','BDCU-3','CH0-CO2','Vol %')].mode().iloc[0]/100
            co2_in_cal3 = bv[('Fermenter03','BDCU-3','CH0-CO2','Vol %')].min()/100

        if not o2_in_cal3:
            o2_in_cal3 = bv[('Fermenter03','BDCU-3','CH1-O2','Vol %')].mode().iloc[0]/100
            o2_in_cal3 = bv[('Fermenter03','BDCU-3','CH1-O2','Vol %')].max()/100
       

    if AF2 is not None:
        if not co2_in_cal2:
            co2_in_cal2 = bv[('Fermenter02','BDCU-2','CH0-CO2','Vol %')].mode().iloc[0]/100
            co2_in_cal2 = bv[('Fermenter02','BDCU-2','CH0-CO2','Vol %')].min()/100

        if not o2_in_cal2:
            o2_in_cal2 = bv[('Fermenter02','BDCU-2','CH1-O2','Vol %')].mode().iloc[0]/100
            o2_in_cal2 = bv[('Fermenter02','BDCU-2','CH1-O2','Vol %')].max()/100
       
    if not co2_in_cal1:
        co2_in_cal1 = bv[('Fermenter01','BDCU-1','CH0-CO2','Vol %')].mode().iloc[0]/100
        co2_in_cal1 = bv[('Fermenter01','BDCU-1','CH0-CO2','Vol %')].min()/100

    if not o2_in_cal1:
        o2_in_cal1 = bv[('Fermenter01','BDCU-1','CH1-O2','Vol %')].mode().iloc[0]/100
        o2_in_cal1 = bv[('Fermenter01','BDCU-1','CH1-O2','Vol %')].max()/100

    
    
    # constants
    R = 8.314472 # [J /mol/K]
    mw_co2 = 44 # g/mol
    mw_o2 = 32 # g/mol


    # Fermenter Three. 
    if AF3 is not None:
        temp = bv[('Fermenter03','BDCU-3','Temperature','°C')]+273.15 # in K
        pres = bv[('Fermenter03','BDCU-3','Pressure','bar')]*100 # kPa
    
    ### calculate CER
    ## formula
    # g/h
    if AF3 is not None:
        CER_3 = pres*mw_co2/(R*temp)*((bv[('Fermenter03','BDCU-3','F_out3','LPM')])*  
                           (bv[('Fermenter03','BDCU-3','CH0-CO2','Vol %')]/100) -
                           (bv[('Fermenter03','BDCU-3','F_in3','LPM')]*co2_in_cal3))*60
    
    
    ### calculate OUR
    ## formula
    # g/h
    if AF3 is not None: 
        OUR_3 = pres*mw_o2/(R*temp)*((bv[('Fermenter03','BDCU-3','F_out3','LPM')])*  
                        (bv[('Fermenter03','BDCU-3','CH1-O2','Vol %')]/100) -
                           (bv[('Fermenter03','BDCU-3','F_in3','LPM')]*o2_in_cal3))*60
    
    
    # Fermenter Two. 
    if AF2 is not None:
        temp = bv[('Fermenter02','BDCU-2','Temperature','°C')]+273.15 # in K
        pres = bv[('Fermenter02','BDCU-2','Pressure','bar')]*100 # kPa
    
    ### calculate CER
    ## formula
    # g/h
    if AF2 is not None:
        CER_2 = pres*mw_co2/(R*temp)*((bv[('Fermenter02','BDCU-2','F_out2','LPM')])*  
                           (bv[('Fermenter02','BDCU-2','CH0-CO2','Vol %')]/100) -
                           (bv[('Fermenter02','BDCU-2','F_in2','LPM')]*co2_in_cal2))*60
    
    
    ### calculate OUR
    ## formula
    # g/h
    if AF2 is not None: 
        OUR_2 = pres*mw_o2/(R*temp)*((bv[('Fermenter02','BDCU-2','F_out2','LPM')])*  
                        (bv[('Fermenter02','BDCU-2','CH1-O2','Vol %')]/100) -
                           (bv[('Fermenter02','BDCU-2','F_in2','LPM')]*o2_in_cal2))*60
    
    ### Fermenter One. 
    temp = bv[('Fermenter01','BDCU-1','Temperature','°C')]+273.15 # in K
    pres = bv[('Fermenter01','BDCU-1','Pressure','bar')]*100 # kPa
    
    
    ### calculate CER
    ## formula
    # g/h
    CER_1 = pres*mw_co2/(R*temp)*((bv[('Fermenter01','BDCU-1','F_out1','LPM')])*  
                       (bv[('Fermenter01','BDCU-1','CH0-CO2','Vol %')]/100) -
                       (bv[('Fermenter01','BDCU-1','F_in1','LPM')]*co2_in_cal1))*60
    
    
    
    ### calculate CER
    ## formula
    # g/h
    OUR_1 = pres*mw_o2/(R*temp)*((bv[('Fermenter01','BDCU-1','F_out1','LPM')])*  
                           (bv[('Fermenter01','BDCU-1','CH1-O2','Vol %')]/100) -
                           (bv[('Fermenter01','BDCU-1','F_in1','LPM')]*o2_in_cal1))*60
    
    bv[('Fermenter01','BDCU-1','OUR','g/h')] = OUR_1
    bv[('Fermenter01','BDCU-1','CER','g/h')] = CER_1
    if AF2 is not None:
        bv[('Fermenter02','BDCU-2','OUR','g/h')] = OUR_2
        bv[('Fermenter02','BDCU-2','CER','g/h')] = CER_2
    
    if AF3 is not None:
        bv[('Fermenter03','BDCU-3','OUR','g/h')] = OUR_3
        bv[('Fermenter03','BDCU-3','CER','g/h')] = CER_3
    
    return bv
    
def read_offGasData(blueVis_filePath, AF1, AF2=None, AF3=None, co2_in_cal1=False,o2_in_cal1=False,co2_in_cal2=False,o2_in_cal2=False,yn_in1=False,yn_in2=False,yn_in3=False):
    '''
    function reads in the offgas data from a bioreactor and returns the calculated CER, OUR, and data. 
    
    inputs:
        blueVis_filePath: 
            string to a csv file.
        AF1: 
            pd.DataFrame() of the airflowrates of bioreactor1. 
        AF1: 
            pd.DataFrame() of the airflowrates of bioreactor2.
        co2_in_cal1:
            float. fraction of carbon dioxide in the inlet gas (reactor 1). 
        co2_in_cal2:
            float. fraction of carbon dioxide in the inlet gas (reactor 1). 
        o2_in_cal1:
            float. fraction of oxygen in the inlet gas (reactor 1).  
        o2_in_cal2:
            float. fraction of oxygen in the inlet gas (reactor 1).      
        yn_in1:
            float. fraction of nitrogen in the inlet gas (reactor 1). 
        yn_in2:
            float. fraction of nitrogen in the inlet gas (reactor 2).
    
    '''
    
    
    
    # read in blueVis off-gas data. 
    blueVisData = pd.read_csv(blueVis_filePath,sep=';',header=[0,1,2,3])
    
    # drop id, serinal number, UTC.
    blueVisData_use = blueVisData.loc[3:,:] # drop id, serial number UTC

    ## convert date-time to 'age' (matching the process data from MFCS#3). 
    # convert datatime format.
    blueVisData_use.loc[:,'Date_Time'] = blueVisData_use.iloc[:,1].apply(lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
    
    # determine time difference between data points. 
    blueVisData_use.loc[:,'temp_age'] = blueVisData_use.loc[:,'Date_Time'].diff()
    
    # convert time difference to seconds. 
    blueVisData_use.loc[:, 'temp_age'] = blueVisData_use['temp_age'].apply(lambda x: x.days*24 + x.seconds/3600)
    
    # set the initial datapoint as time 0. 
    blueVisData_use.loc[blueVisData_use.index[0], 'temp_age'] = 0
    
    # calculate a running age for the process. 
    blueVisData_use.loc[:, 'age'] = blueVisData_use['temp_age'].cumsum()
   
    # resort the index. 
    blueVisData_use = blueVisData_use.sort_index(axis=1)

    ##### calculate the fraction of N2 in the offgas.
    #### N2 is inert.
    ### ASSUMPTION: No humidity in the in flow (not measured).
    ## y_{N2,out} = 1 - y_{O_2,out} -y_{CO_2,out} - y_{H_2O,out}
    # reactor 2

    if AF3 is not None:
        yn3_out = 1-(blueVisData_use[('Fermenter03','BDCU-3','CH0-CO2','Vol %')]+ # co2 out (channel 0)
                     blueVisData_use[('Fermenter03','BDCU-3','CH1-O2','Vol %')]+ # o2 out (channel 1)
                     blueVisData_use[('Fermenter03','BDCU-3','Abs_Hum','Vol %')])/100  # absolute humidity
    

    if AF2 is not None:
        yn2_out = 1-(blueVisData_use[('Fermenter02','BDCU-2','CH0-CO2','Vol %')]+ # co2 out (channel 0)
                     blueVisData_use[('Fermenter02','BDCU-2','CH1-O2','Vol %')]+ # o2 out (channel 1)
                     blueVisData_use[('Fermenter02','BDCU-2','Abs_Hum','Vol %')])/100  # absolute humidity
    
    # reactor 1
    yn1_out = 1-(blueVisData_use[('Fermenter01','BDCU-1','CH0-CO2','Vol %')]+
                 blueVisData_use[('Fermenter01','BDCU-1','CH1-O2','Vol %')]+
                 blueVisData_use[('Fermenter01','BDCU-1','Abs_Hum','Vol %')])/100
    
    ## determine fraction of N2 in the in gas. 
    # based on the mode of the reactor reading.
    if AF3 is not None:
        if not yn_in3:
            #yn_in2 = yn2_out.mode().iloc[0]
            yn_in3 = yn3_out.max()
            

    if AF2 is not None:
        if not yn_in2:
            #yn_in2 = yn2_out.mode().iloc[0]
            yn_in2 = yn2_out.max()
            
    if not yn_in1:
        #yn_in1 = yn1_out.mode().iloc[0]
        yn_in1 = yn1_out.max()

    # ratio of nitrogen percentage in and out.
    ratio_flow1 = yn_in1/yn1_out
    #ratio_flow1 = 1


    if AF3 is not None:
        ratio_flow3 = yn_in3/yn3_out
        #ratio_flow2 = 1
    if AF2 is not None:
        ratio_flow2 = yn_in2/yn2_out
        #ratio_flow2 = 1

    # assign to the dataframe. 
    if AF3 is not None:
        blueVisData_use[('Fermenter03','BDCU-3','Ratio3','Unitless')] = ratio_flow3
    if AF2 is not None:
        blueVisData_use[('Fermenter02','BDCU-2','Ratio2','Unitless')] = ratio_flow2
    
    blueVisData_use[('Fermenter01','BDCU-1','Ratio1','Unitless')] = ratio_flow1
    
    # assign appropriate gas flow rates to the off gas data (aligning the timepoints. )
    df = merge_dfs(blueVisData_use,AF1,AF2,AF3)

    ## calculate flow rates out. 
    # ratio * in and out.

    if AF3 is not None:
        F_out3 = df[('Fermenter03','BDCU-3','F_in3','LPM')]*df[('Fermenter03','BDCU-3','Ratio3','Unitless')]
        df[('Fermenter03','BDCU-3','F_out3','LPM')]=F_out3
    if AF2 is not None:
        F_out2 = df[('Fermenter02','BDCU-2','F_in2','LPM')]*df[('Fermenter02','BDCU-2','Ratio2','Unitless')]
        df[('Fermenter02','BDCU-2','F_out2','LPM')]=F_out2

        
        
    F_out1 = df[('Fermenter01','BDCU-1','F_in1','LPM')]*df[('Fermenter01','BDCU-1','Ratio1','Unitless')]
    df[('Fermenter01','BDCU-1','F_out1','LPM')] = F_out1
    
    # call function to calculate the CER, OUR for the fermenters.
    df = calc_offgas(df,AF2,AF3,co2_in_cal1,o2_in_cal1,co2_in_cal2,o2_in_cal2)
    
    return(df)

def read_file(file):#,outputFile,numberFile):
    '''
    function that takes a file, opens the file and extracts bioprocess data.
    
    # file - text files generated from the MFCS exported data.
    
    outputs.
        variable - string
            bioprocess variable (temp, pO2, agitation, etc.)
        date - list
            day of recording
        time - list
            (time during the day, recourded)
        age - list
            age (h) of the reactor.
        value - list
            list of values
    
    '''
    with open(file, 'r') as fd:
        
        
        # variable for whether the header (comments) have been passed.
        startData = False
        
        # variable to indicate when data needs to be recorded.
        initData = False
        
        # holding input data.
        date, time, age, value = [],[],[],[]
        
        # iterate over lines.
        iterator = iter(fd)

        for line in iterator:
            # skip blank lines.
            if line.startswith("\n"):
                pass
            
            else:
#                 line = line.strip("Raw")
                
                # 
                if line.startswith(" Raw"):
                    startData = True
                    variable = line.split()[1]
                    #print(variable)

                if startData == True:
#                     print(line)
                    
                    line = line.split()

                    # get the name as "setpoint" or "variable" for each item.
                    if line[0]=='Data':
                        #print('4',line)
                        next_line = next(iterator)
                        next_line = next_line.strip()
                        variable = variable+"_"+next_line
                        #print('Next line:', next_line.strip(),variable) 
                        
                        

#                     print(len(line))
                    
                    # start of recorded data.    
                    if line[0] == "Date":
                        initData=True
                    
                    if initData==True:
                        if line[0] == "Date":
                            pass
                        # record data

                        else:
                            date.append(line[0])
                            time.append(line[1])
                            age.append(float(line[2]))
                            value.append(float(line[3]))
    fd.close()
    return(variable,date,time,age,value)
    