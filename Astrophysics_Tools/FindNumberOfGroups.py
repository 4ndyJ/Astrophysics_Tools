'''
for a given JWST raw image, the data set for the science target or the reference image, ends up having more flux. This is due to various factors.
The two biggest factors are the spectral type (which for the MIRI instrument is less of a problem since this is in the releigh-jeans tail of the SED), and the number of groups in the itegration.
Matching the brightness/counts in the two images can be done as shown:
'''
from astropy.io import fits
import numpy as np

def FindNumGroups(RefPath, SciPath, IsSciBrighter, KernelPix=15, Method="Summed", verbose=True):
    '''
    Inputs:
        RefPath (Str) : the file path to A reference image.
        SciPath (Str) : The file path to th Science image.
        IsSciBrighter (Bool) : by default the Reference image is brighter (It was the first case I tested for, But the code works just as well if the image was the other way around. Since once the files are loaded in, its just variable names)
        KernelPix (int) : defines a 2*KernelPix+1 side length square around the centre pixel defined in the .fits image. 
        Method (Str) : {MaxPixel, Summed, Summed+Nan} Currently two methods plus an argument to ignore values below a specific level.
            MaxPixel : Compares the two images to see when the max pixel has the same counts
            Summed : Sums all the values in the kernel, and matches this value
            Nan : an argument passed onto Summed (Summed+Nan) to ignore values below half the max pixel count (Used to better focus on the lobes of the Miri images.)

    Returns:
        minimizedGroups (int) : the number of frame of the image cube which is nomininally brighter at the final frame. Can be used to slice the image with algorithms compatable, such as spaceKLIP
    '''
    if IsSciBrighter:
        RefPath, SciPath = SciPath, RefPath  # Code assumes Reference images are brighter, so will cycle through those, but the science images
                                            # could be brighter, SpaceKLIP allows for the selection Sci or Ref images to be cropped in this way
                                            # so just swap around the Refpath and SciPath, and code works fine

    hdul_Ref = fits.open(RefPath)
    hdul_Sci = fits.open(SciPath)

    integration_Ref = 0  # Just chose the first integration. THis could be changed?
    integration_Sci = 0

    group_Ref = int(hdul_Ref["SCI"].header["NAXIS3"])  # How many total groups are there?
    group_Sci = int(hdul_Sci["SCI"].header["NAXIS3"])

    Cx = int(hdul_Ref["SCI"].header["CRPIX1"])  # Centre pix location for image (centred on PSF not frame)
    Cy = int(hdul_Ref["SCI"].header["CRPIX2"])

    SciCube = hdul_Sci["SCI"].data[integration_Sci, group_Sci - 1]  # Load the Science Cube

    SciCubeCrop = SciCube[(Cy - KernelPix):(Cy + KernelPix), (Cx - KernelPix):(Cx + KernelPix)]  # Crop it around the central PSF
    if "Nan" in Method:
        SciCubeCrop = np.where(SciCubeCrop > np.max(SciCubeCrop) // 2, SciCubeCrop, np.nan)  # Get rid of data that isnt at least half the max pixel
                                                                                             # this is to isolate the PSF better?
    Nminimized = np.inf  # Large number used for minimisation.
    minimizedGroups = None
    minimized = None

    for i in range(group_Ref):
        RefCube = hdul_Ref["SCI"].data[integration_Ref, i]  # load cube
        RefCubeCrop = RefCube[(Cy - KernelPix):(Cy + KernelPix), (Cx - KernelPix):(Cx + KernelPix)]  # crop it
        if "Summed" in Method:
            if "Nan" in Method:
                RefCubeCrop = np.where(RefCubeCrop > np.max(RefCubeCrop) // 2, RefCubeCrop, np.nan)  # delete unrelated data
            SubtractedCube = SciCubeCrop - RefCubeCrop  # take reference layer from Science layer
            summed = np.nansum(SubtractedCube)  # add up total flux
            if summed < Nminimized and summed > 0:  # minimize total flux. making sure total flux is still above 0 (could have over subtraction issues still)
                Nminimized = summed
                minimizedGroups = i
                minimized = SubtractedCube
        elif Method == "MaxPixel":
            if np.nanmax(SciCubeCrop) < np.nanmax(RefCubeCrop):  # when any pixel's counts is larger than any pixels count, then return that image
                if verbose:
                    print(f"Optimized Groups using {Method} is: {i}")
                return i
    if verbose:
        print(f"Optiimized Groups using {Method} is: {minimizedGroups}")
    return minimizedGroups  # return frame that minimizes the total flux
