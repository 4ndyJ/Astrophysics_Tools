import glob
import os
from astropy.io import fits
import numpy as np
import re
import subprocess

def Find_File_Types(init_path, file_types = ["Background", "Science", "Reference", "TA"], verbose = True):
	'''Finds all the files of specified types in a directory and returns them as lists.'''
	def Find_Backgrounds(fits_files):
		'''
		Finds all the background files in a directory, and returns them as a list.
		
		Args:
			init_path (str): The path to the directory containing the files.
		
		Returns:
			list: A list of paths to the background files.
		'''
		_background_files = []
		for fits_file in fits_files:
			header = fits.getheader(fits_file, ext = 0)
			if header.get('BKGDTARG', False):
				_background_files.append(fits_file)	
		return _background_files

	def Find_Science(fits_files):
		'''
		Finds all the science files in a directory, and returns them as a list.
		
		Args:
			init_path (str): The path to the directory containing the files.
		
		Returns:
			list: A list of paths to the science files.
		'''
		_science_files = []
		for fits_file in fits_files:
			header = fits.getheader(fits_file, ext = 0)
			if not header.get('IS_PSF') and not header.get('BKGDTARG', False) and not header.get("EXP_TYPE", "").endswith("ACQ"):
				_science_files.append(fits_file)	
		return _science_files

	def Find_References(fits_files):
		'''
		Finds all the reference files in a directory, and returns them as a list.
		
		Args:
			init_path (str): The path to the directory containing the files.
		
		Returns:
			list: A list of paths to the reference files.
		'''
		_reference_files = []
		for fits_file in fits_files:
			header = fits.getheader(fits_file, ext = 0)
			if header.get('IS_PSF') and not header.get('BKGDTARG', False):
				_reference_files.append(fits_file)
		return _reference_files
	

	def Find_Target_Acquisitions(fits_files):
		'''
		Finds all the target acquisition files in a directory, and returns them as a list.
		
		Args:
			init_path (str): The path to the directory containing the files.
		
		Returns:
			list: A list of paths to the target acquisition files.
		'''
		_target_acquisition_files = []
		for fits_file in fits_files:
			header = fits.getheader(fits_file, ext = 0)
			if header.get("EXP_TYPE", "").endswith("ACQ"):
				_target_acquisition_files.append(fits_file)
		return _target_acquisition_files
	

	fits_files = glob.glob(os.path.join(init_path, '*.fits'))
	for file_type in file_types:
		if file_type == "Background":
			background_files = Find_Backgrounds(fits_files)
			if verbose:
				print(f"Found {len(background_files)} background files.")
		elif file_type == "Science":
			science_files = Find_Science(fits_files)
			if verbose:
				print(f"Found {len(science_files)} science files.")
		elif file_type == "Reference":
			reference_files = Find_References(fits_files)
			if verbose:
				print(f"Found {len(reference_files)} reference files.")
		elif file_type == "TA":
			target_acquisition_files = Find_Target_Acquisitions(fits_files)
			if verbose:
				print(f"Found {len(target_acquisition_files)} target acquisition files.")
		else:
			if verbose:
				print(f"Unknown file type: {file_type}")

	# Return all found files
	returns_dict = {"Background": locals().get('background_files', []),
					"Science": locals().get('science_files', []),
					"Reference": locals().get('reference_files', []),
					"TA": locals().get('target_acquisition_files', [])}
	return returns_dict


def Get_Contrast_Separation_From_Calcon(calcon_dir, differential_imaging_method = "ADI+RDI", 
										number_of_annuli = 1, number_of_subsections = 1, 
										include_transmistion_mask = True, verbose = True):
	'''
	Extracts contrast and separation data from a calcon file.
	Args:
		calcon_dir (str): The directory containing the calcon file.
		differential_imaging_method (str): The differential imaging method used.
		number_of_annuli (int): The number of annuli used in the analysis.
		number_of_subsections (int): The number of subsections used in the analysis.
		include_transmistion_mask (bool): Whether to include the transmission mask in the analysis.
		verbose (bool): Whether to print verbose output.
	Returns:
		tuple: A tuple containing the contrast and separation data.
	'''

	#find the files
	glob_path = f"{calcon_dir}/{differential_imaging_method}_NANNU{number_of_annuli}_NSUBS{number_of_subsections}*-KLmodes-all_cal_"
	if include_transmistion_mask:
		contrast_path = glob.glob(glob_path + "maskcons.npy")[0]
	else:
		contrast_path = glob.glob(glob_path + "cons.npy")[0]
	if verbose:
		print(f"loading {contrast_path}")

	separation_arcsec_path = glob.glob(glob_path + "seps.npy")[0]
	if verbose:
		print(f"loading {separation_arcsec_path}")
	
	
	#load the data
	contrast = np.load(contrast_path)
	separation_arcsec = np.load(separation_arcsec_path)
	
	#find the KL modes:
	injection_file = glob.glob(f"{calcon_dir}/{differential_imaging_method}_NANNU{number_of_annuli}_NSUBS{number_of_subsections}*/*.fits")[0]
	header = fits.getheader(injection_file)
	klmode_keys = [key for key in header if re.match(r"KLMODE\d+$",key)]
	klmode_values = [header[key] for key in klmode_keys]

	return contrast, separation_arcsec, klmode_values

