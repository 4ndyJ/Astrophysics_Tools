from astropy.io import fits
# from spaceKLIP import starphot
import numpy as np
from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import SkyCoord
from .Function_Tools import enforce_types


# def Contrast_To_Magnitude(Star,Instrument,Filter,SEDFile,Cons):
#     try:
#         Simbad.query_object(Star)["SP_TYPE"]
#     except:
#         Simbad.add_votable_fields("sptype")
#     Spectral_Type=Simbad.query_object(Star)["SP_TYPE"]
#     mstar,_ = starphot.get_stellar_magnitudes(SEDFile,Spectral_Type,Instrument)
#     ConsAbsMag=mstar[Filter]-2.5*np.log10(Cons) #this is the only line Im not confident in. 
#     return ConsAbsMag


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


def arcsecond_separation_between_two_objects(Object1, Object2):
    '''
    Returns the separation of two objects in arcseconds
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
    coord1 = SkyCoord(ra=ra1, dec=dec1, unit=(u.hourangle, u.deg)) # type: ignore - astropy coordinates are not type checked by code editor
    coord2 = SkyCoord(ra=ra2, dec=dec2, unit=(u.hourangle, u.deg)) # type: ignore - astropy coordinates are not type checked by code editor

    # Calculate the separation in arcseconds
    separation = coord1.separation(coord2).arcsecond
    return separation

def Convert_Between_Arcsec_and_AU(distance_pc=None, separation_arcsec=None, separation_au=None):
    '''
    Converts between arcsecond separation and Astronomical Units (AU) based on distance in parsecs.
    
    Inputs:
        distance_pc (float): Distance in parsecs
        sep_arcsec (float, optional): Separation in arcseconds. If provided, separation_au will be calculated.
        sep_au (float, optional): Separation in AU. If provided, sep_arcsec will be calculated.

    Returns:
        float: Either the separation in arcseconds or AU, depending on the input provided.
    '''
    def Arcsec_to_AU(_separation_arcsec, _distance_pc):
        return _separation_arcsec * _distance_pc

    def AU_to_Arcsec(_separation_au, _distance_pc):
        return _separation_au / _distance_pc

    if separation_arcsec is not None:
        return Arcsec_to_AU(separation_arcsec, distance_pc)
    elif separation_au is not None:
        return AU_to_Arcsec(separation_au, distance_pc)
    else:
        raise ValueError("Either separation_arcsec or separation_au must be provided.")
    

def Wiens_Law_Microns(temperature_K):
    '''
    Returns the wavelength of peak emission for a black body at a given temperature using Wien's Law.
    
    Inputs:
        Temperature (float): Temperature in Kelvin
    Returns:
        float: Wavelength in microns (um)
    '''
    b = 2.8977729e-3  # Wien's displacement constant in m*K
    return b / temperature_K * 1e6  # Convert to microns


@enforce_types
def Cookie_Cutter_Mask(data: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    A mask of the same shape as the data is applied to the data
    There are strict requirements on the mask type:
        - The mask must be a binary mask
            - 1s indicate the region to keep, 0s indicate the region to mask
            - if the mask is not binary, values above 0 are treated as 1s, all other values (invluding NaNs) are treated as 0s
        - the masked region must have a defined shape (e.g., circular, rectangular)
            - i.e., after application of the mask, the data should still be a 2D array
    Parameters:
        data (np.ndarray): The data to be masked.
        mask (np.ndarray): The binary mask to be applied to the data.
    Returns:
        np.ndarray: The masked data.
    """
    if data.shape != mask.shape:
        raise ValueError("Data and mask must have the same shape.")
    if data.ndim != 2 or mask.ndim != 2:
        raise ValueError("Data and mask must be 2D arrays.")


    mask = np.where(mask > 0, 1, 0)  # Convert to binary mask, deals with NaNs aswell

    # find the bounding box of the masked region
    y_indices, x_indices = np.where(mask)
    ymin, ymax = y_indices.min(), y_indices.max() + 1
    xmin, xmax = x_indices.min(), x_indices.max() + 1


    # cut out the region of interest from the data and mask
    cut_out_data = data[ymin:ymax, xmin:xmax]
    cut_out_mask = mask[ymin:ymax, xmin:xmax]

    # apply the mask to the cut out data
    masked_applied_data = cut_out_data * cut_out_mask

    return masked_applied_data

