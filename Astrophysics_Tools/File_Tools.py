import glob
import os
from astropy.io import fits

def Find_File_Types(init_path, file_types = ["Background", "Science", "Reference","TA"], verbose = True):
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
	return locals().get('background_files', []), locals().get('science_files', []), locals().get('reference_files', []), locals().get('target_acquisition_files', [])
