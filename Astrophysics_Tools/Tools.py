import numpy as np

import astropy
import astropy.units as u
from astropy import table
from astropy.coordinates import SkyCoord

from astroquery.simbad import Simbad
from astroquery.mast import Observations

#Type hints
from .Function_Tools import enforce_types
from typing import cast, Callable





def Ballesteros(B,V):
    return 4600*(1/(0.92*(B-V)+1.7)+1/(0.92*(B-V)+0.62))


def arcsecond_separation_between_two_objects(Object1: str, Object2: str) -> float:

    if Object1 is None or Object2 is None:
        raise ValueError("Both Object1 and Object2 must be provided.")
    Simbad_Query = Simbad()

    ra_str = "RA" if astropy.__version__ <= '0.4.7' else "ra"
    dec_str = "DEC" if astropy.__version__ <= '0.4.7' else "dec"


    binary1_data = Simbad_Query.query_object(Object1) 
    if binary1_data is None or len(binary1_data) == 0:
        raise ValueError(f"Could not retrieve data for {Object1}")
    
    ra1 = binary1_data[ra_str][0]  # Right Ascension
    dec1 = binary1_data[dec_str][0]  # Declination

    binary2_data = Simbad_Query.query_object(Object2) 
    if binary2_data is None or len(binary2_data) == 0:
        raise ValueError(f"Could not retrieve data for {Object2}")
    
    ra2 = binary2_data[ra_str][0]  # Right Ascension
    dec2 = binary2_data[dec_str][0]  # Declination

    # Convert RA and Dec to SkyCoord object 
    coord1 = SkyCoord(ra=ra1, dec=dec1, unit=(u.hourangle, u.deg)) # type: ignore - astropy coordinates are not type checked by code editor
    coord2 = SkyCoord(ra=ra2, dec=dec2, unit=(u.hourangle, u.deg)) # type: ignore - astropy coordinates are not type checked by code editor

    # Calculate the separation in arcseconds
    separation = coord1.separation(coord2).to(u.arcsecond).value #type: ignore - astropy coordinates are not type checked by code editor
    return separation

def Convert_Between_Arcsec_and_AU(distance_pc=None, separation_arcsec=None, separation_au=None):

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
    b = 2.8977729e-3  # Wien's displacement constant in m*K
    return b / temperature_K * 1e6  # Convert to microns


@enforce_types
def Cookie_Cutter_Mask(data: np.ndarray, mask: np.ndarray) -> np.ndarray:

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



def get_observations(target_name: str, instrument: str = "JWST") -> table.Table:
    # Recast functions that dont support type hints
    Observations.list_missions = cast(Callable[[], list[str]], Observations.list_missions)

    query = Simbad()
    result = query.query_object(target_name)
    if result is None:
        print(f"Target '{target_name}' not found in SIMBAD.")
        return table.Table()
    target_name = result['main_id'][0]

    
    if instrument.upper() not in Observations.list_missions():
        raise ValueError(f"Instrument \"{instrument}\" is not supported.\n\
                         Supported instruments are:\n {Observations.list_missions()}")

    obs_table = Observations.query_criteria(objectname=target_name, obs_collection=instrument) # type: ignore

    if len(obs_table) == 0:
        print(f"No JWST observations found for {target_name}.")
        return table.Table()
    return obs_table


def get_observed_filters_from_mast(target_name: str, instrument: str = "JWST") -> list[str]:

    obs_table = get_observations(target_name = target_name, instrument = instrument)
    
    filters = set(obs_table["filters"]) #type: ignore
    filter_names = set()
    if instrument.upper() != "JWST":
        return list(filters) 
    for filt in filters:
        filter_name, pupil_mask = filt.split(';')
        filter_names.add(filter_name)
        
    return sorted(list(filter_names))

