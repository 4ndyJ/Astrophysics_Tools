import numpy as np
from astropy.table import table

from .Function_Tools import enforce_types


def Ballesteros(B: float, V: float) -> float:
    '''
    Returns an approximation for the temperature of an object in Kelvin, given its B and V magnitudes
    Inputs
    B (float): B magnitude
    V (float); V magnitude

    returns:
    Calculated Temperature (K)
    '''
    ...
def arcsecond_separation_between_two_objects(Object1: str, Object2: str) -> np.float64:
    '''
    Returns the separation of two objects in arcseconds
    Inputs
    Object1 (Str): Simbad Queriable Object
    Object2 (Str): Simbad Queriable Object

    Returns:
    separation (float: u.arcsecond): Separation in arcseconds with astropy unit arcsecond
    '''
    ...
def Convert_Between_Arcsec_and_AU(distance_pc: float, separation_arcsec: float | None = None, separation_au: float | None = None) -> float:
    '''
    Converts between arcsecond separation and Astronomical Units (AU) based on distance in parsecs.
    
    Inputs:
        distance_pc (float): Distance in parsecs
        sep_arcsec (float, optional): Separation in arcseconds. If provided, separation_au will be calculated.
        sep_au (float, optional): Separation in AU. If provided, sep_arcsec will be calculated.

    Returns:
        float: Either the separation in arcseconds or AU, depending on the input provided.
    '''
    ...
def Wiens_Law_Microns(temperature_K : float) -> float:
    '''
    Returns the wavelength of peak emission for a black body at a given temperature using Wien's Law.
    
    Inputs:
        Temperature (float): Temperature in Kelvin
    Returns:
        float: Wavelength in microns (um)
    '''
    ...
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
    ...
def get_observations(target_name: str, instrument: str = "JWST") -> table.Table: ...
def get_observed_filters_from_mast(target_name: str, instrument: str = "JWST") -> list[str]: ...
