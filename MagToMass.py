
import glob
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import numpy as np
from astropy import constants as const
import os

def Load_Models(Instrument=None,Mask=None):
    Main_File_Path=os.environ["ATMO_2020_MODELS"]+"evolutionary_tracks/ATMO_CEQ/JWST_coronagraphy/"
    if Instrument.upper() == "MIRI":
        FilePath=Main_File_Path+"JWST_coron_MIRI"
    elif Instrument.upper() == "NIRISS":
        FilePath=Main_File_Path+"JWST_coron_NIRISS"
    elif Instrument.upper() == "NIRCAM":
        try:
            Mask.upper()
        except:
            print("Type Error with Mask... Resetting")
            Mask=""
        if Mask.upper() not in ["MASK210R","MASK335R","MASK430R","MASKLWB","MASKSWB"]:
            print("A not supported mask was entered, Assuming MASK335R")
            Mask = "MASK335R"

        FilePath=Main_File_Path+"JWST_coron_NIRCAM_"+Mask.upper()
    else:
        FilePath = None

    return(FilePath)

def Mag_to_Mass(Age_Estimate,MagToFind,Filter="NIRCAM-F444W",Instrument="NIRCAM",Mask="MASK335R",Verbose=True):
    skipped=0
    FilePath = Load_Models(Instrument,Mask)
    if FilePath == None:
        return("No file Path")
        
        
    Age_Estimate/=1000 # conversion to Units of GYR from MYR input
    MagMassForAge=[]
    for f in glob.glob(FilePath+"/*.txt"):
        Data=pd.read_csv(f,header=0,delim_whitespace=True)
        df=ReshapeData(Data)
        if Age_Estimate < float(df["Age"][0]) or Age_Estimate > float(df["Age"][len(df["Age"])-1]):
            print("Age is outside of the model's range")
            break
        df_closest = df.iloc[(df['Age'].astype(float)-Age_Estimate).abs().argsort()[:2]]
        
        Mag_in_Filter=df[Filter.upper()].astype(float).tolist()
        Ages=df["Age"].astype(float).tolist()
        Ages,Mag_in_Filter=RemoveZerosFromConnectedList(Ages,Mag_in_Filter)
        
        if Age_Estimate < min(Ages) or Age_Estimate > max(Ages):
            skipped+=1
        else:
            MagMassForAge+=[(InterpolateTheData(Age_Estimate,Ages,Mag_in_Filter),float(df["Mass"][0]))]
    
    Mag,Mass=zip(*sorted(MagMassForAge))
    if Verbose:
        print(f"{skipped} Files were skipped during the interpolation since the tabulated data did not contain the age ({Age_Estimate} Gyr) Specifed")
    return InterpolateTheData(MagToFind,Mag,Mass)*const.M_sun/const.M_jup

def ReshapeData(df):
    new_df = pd.DataFrame([i[:-1] for i in df[1:].values.tolist()],columns =list(df.keys()[1:]))
    return(new_df)

def RemoveZerosFromConnectedList(List1,List2):
    OutputListZipped=[]
    for i,j in zip(List1,List2):
        if i !=0 and j != 0:
            OutputListZipped+=[(i,j)]
    return zip(*OutputListZipped)
    
def InterpolateTheData(Nearest,xi,yi,steps=1000,order=1):
    x=np.linspace(min(xi),max(xi),steps)
    s=IUS(xi,yi)
    y=s(x)
    return y[min(range(len(x)), key=lambda i: abs(x[i]-Nearest))]
