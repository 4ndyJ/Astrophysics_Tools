from astropy.io import fits
from spaceKLIP import starphot
import numpy as np
from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import SkyCoord


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


def arcsecond_separation(Object1, Object2):
    '''
    Returns the separation of two objects in arcsecons
    Inputs
    Object1 (Str): Simbad Queriable Object
    Object2 (Str): Simbad Queriable Object

    Returns:
    separation (float: u.arcsecond): Separation in arcseconds with astropy unit arcsecond
    '''

    Simbad_Query = Simbad()

    binary1_data = Simbad_Query.query_object(Object1) 
    ra1 = binary1_data['RA'][0]  # Right Ascension
    dec1 = binary1_data['DEC'][0]  # Declination

    binary2_data = Simbad_Query.query_object(Object2)  
    ra2 = binary2_data['RA'][0]  # Right Ascension
    dec2 = binary2_data['DEC'][0]  # Declination

    # Convert RA and Dec to SkyCoord object 
    coord1 = SkyCoord(ra=ra1, dec=dec1, unit=(u.hourangle, u.deg))
    coord2 = SkyCoord(ra=ra2, dec=dec2, unit=(u.hourangle, u.deg))

    # Calculate the separation in arcseconds
    separation = coord1.separation(coord2).arcsecond
    return separation
