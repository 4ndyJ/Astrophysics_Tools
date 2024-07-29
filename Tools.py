from astropy.io import fits
from spaceKLIP import starphot
import numpy as np
from astroquery.simbad import Simbad


def KLModeList(idir):
    hdul=fits.open(idir)
    Header=hdul[0].header
    return [(int(x.split("KLMODE")[1]),Header[x]) for x in Header.keys() if "KLMODE" in x]



def Contrast_To_Magnitude(Star,Instrument,Filter,SEDFile,Cons):
    try:
        Simbad.query_object(Star)["SP_TYPE"]
    except:
        Simbad.add_votable_fields("sptype")
    Spectral_Type=Simbad.query_object(Star)["SP_TYPE"]
    mstar,_ = starphot.get_stellar_magnitudes(SEDFile,Spectral_Type,Instrument)
    ConsAbsMag=mstar[Filter]-2.5*np.log10(Cons) #this is the only line Im not confident in. 
    return ConsAbsMag


def Ballesteros(B,V):
    '''
    Returns an approximation for the temperature of an object in Kelvin, given its B and V magnitudes
    Inputs
    B (float): B magnitude
    V (float); V magnitude

    returns:
    Calculated Temperature (K)
    '''
    return 4600*(1/(0.92*(B-V)+1.7)+1/(0.92*(B-V)+0.62))
