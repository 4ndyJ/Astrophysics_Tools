
import glob
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import numpy as np
from astropy import constants as const
import os

def Load_Models(Instrument=None,Mask=None):
    '''
    '   Load_Models, as it says on the tin, loads a "selection" (will add more later) of astrophysical models of planets/brown dwarfs/stars
    '
    '   Inputs:
    '       Instrument (str): - Use to distinguish which subsection of the models you are using
    '       Mask (str): - If you are using NIRCam, then the models are tabuled for different coronographic masks.
    '
    '   Returns:
    '       FilePath (str): - An Updated file path containing the models best fit for use.
    '''

    
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
    
    '''
    '    Mag to Mass is the main body of this code, taking inputs and controls the rest of the functions.
    '    The user may suggest an age to fit the models to, and an absolute magnitude to find the best mass for
    '
    '    Inputs:
    '        Age_Estimate (float):    Estimate of the age of the system you are fitting an evolutionary model to
    '        MagToFind (float):       The absolute magnitude of the object or contrast curve to be converted to mass
    '        Filter (str):            In the same format as the models
    '        Instrument (str/None):   Used for file handling
    '        Mask (str/None):         Mask used for the observation if any
    '        Verbose (bool):          Errors could occour with finding tabulated ages, when True, this will output the
    '                                 the number of files skipped for this reason
    '
    '    Returns:
    '        (float):                 In Jupiter masses, the mass of the object with sepeficied absolute magnitude, at
    '                                 the specified age
    '''

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
    
    Mag,Mass=zip(*sorted(MagMassForAge)) #The data needs to be sorted to be interpolated
    if Verbose:
        print(f"{skipped} Files were skipped during the interpolation since the tabulated data did not contain the age ({Age_Estimate} Gyr) Specifed")
    return InterpolateTheData(MagToFind,Mag,Mass)*const.M_sun/const.M_jup

def ReshapeData(df):
    """
    '    ReshapeData takes a dataframe that has a "#" in the first 2 coloumns, since the models seem to have this, removes it and combines the data back
    '    
    '    Inputs:
    '        df (pandas.DataFrame):         Misshapen Dataframe
    '    
    '    Returns:
    '        new_df (pandas.DataFrame):     Recombind Dataframe
    """
    
    new_df = pd.DataFrame([i[:-1] for i in df[1:].values.tolist()],columns =list(df.keys()[1:]))
    return(new_df)

def RemoveZerosFromConnectedList(List1,List2):
    '''
    '    Some filters in have tabiulated magnitudes that are 0 for the wrong reasons. This takes care of that
    '    
    '    Inputs:
    '        List1, List2 (list):     Connected lists, which when removing a zero from one, the corresponding datapoint also needs to be removed
    '    
    '    Returns:
    '        (zip object):            two lists that have their respective zeros removed.
    '''
    OutputListZipped=[]
    for i,j in zip(List1,List2):
        if i !=0 and j != 0:
            OutputListZipped+=[(i,j)]
    return zip(*OutputListZipped)
    
def InterpolateTheData(Nearest,xi,yi,steps=1000,order=1):
    '''
    '    For a given data, find a spline that fits it, and record the closest value of the spline to the wanted value
    '    
    '    Inputs:
    '        Nearest (float):         A float for the value which you are trying to fit to
    '        xi,yi (list):            Lists of the data you are wanting a spline to be fitted to
    '        steps (int):             the number of steps to be used in a linspace, describes the precision of the splines fit to the nearests value.
    '        order (int, {1,2,3}):    the largest power in the spline that will be used
    '
    '    Returns:
    '        (float):                 The value of the spline that is closest to the Desired value
    '''
    x=np.linspace(min(xi),max(xi),steps)
    s=IUS(xi,yi)
    y=s(x)
    return y[min(range(len(x)), key=lambda i: abs(x[i]-Nearest))]
