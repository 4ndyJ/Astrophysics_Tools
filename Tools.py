from astropy.io import fits
def KLModeList(idir):
    hdul=fits.open(idir)
    Header=hdul[0].header
    return [(int(x.split("KLMODE")[1]),Header[x]) for x in Header.keys() if "KLMODE" in x]
