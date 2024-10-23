from pathlib import Path
import time
import os
import numpy as np
from astropy.io import fits
import h5py
import shutil
import psutil


DATA_PATH = Path('C:/Users/quade/Documents/Plato_Storage')

years = range(2026, 2027)

# Quartale
quarters = ['q1', 'q2', 'q3', 'q4']
data_layers = ['l1', 'l2', 'l3']

l1_x = 100
l1_y = 100

l2_x = 8000
l2_y = 8000

l3_x = 800
l3_y = 800
l3_z = 1000

count_simulated_targets = 3
count_simulated_days = 10 

duration_l1_days = duration_l1_90_day_stitch = datasets_l1_day = datasets_l1_stitch = datasets_l2 = datasets_l3 = 0
    
### Calculate nesseccary variables

# max_target_dir is the last / highest sub directory 
max_target_dir = count_simulated_targets - count_simulated_targets % -10000

# Calculate one data set and determine the size
# The file size is not calculated but read from the file system to include headers etc.
# This is done once at the start of the script to ensure no (wrong) static values are used for 
# bandwith calculation.

targets_dir_path = DATA_PATH
print(f'Generating L1-L3 once to determine writablity to the file system and file sizes.')

# obj_Disk = psutil.disk_usage('C:')
# print (obj_Disk.total / (1024.0 ** 3))
# print (obj_Disk.used / (1024.0 ** 3))
# print (obj_Disk.free / (1024.0 ** 3))
# print (obj_Disk.percent)

## L1 - 1 day
data = np.random.random((l1_x, l1_y))
fits_data = fits.PrimaryHDU(data)
file_name = 'l1_day.fits'
try:
    fits_data.writeto(targets_dir_path / file_name, overwrite=True)
except:
    print("File System not writable")
file_stats = os.stat(targets_dir_path / file_name)
filesize_l1_day = file_stats.st_size
os.remove(targets_dir_path / file_name)
print('--- File Sizes ---')
print(f'L1-1: {(filesize_l1_day / 1024):.1f} kB') 

## L1 - 90 days
data = np.random.random((l1_x, l1_y * count_simulated_days))
fits_data = fits.PrimaryHDU(data)
file_name = 'l1_90_days.fits'
fits_data.writeto(targets_dir_path / file_name, overwrite=True)
file_stats = os.stat(targets_dir_path / file_name)
filesize_l1_90_day_stitch = file_stats.st_size
os.remove(targets_dir_path / file_name)
print(f'L1-90: {filesize_l1_90_day_stitch / (1024 * 1024):.1f} MB')

# ## L2
# data = np.random.rand(l2_x, l2_y)
# file_name = 'l2.h5'
# with h5py.File(targets_dir_path / file_name, 'w') as hf:
#     hf.create_dataset("dataset_1", data=data)
# file_stats = os.stat(targets_dir_path / file_name)
# filesize_l2 = file_stats.st_size
# os.remove(targets_dir_path / file_name)
# print(f'L2: {filesize_l2 / (1024 * 1024 * 1024):.1f} GB')

# ## L3
# data = np.random.rand(l3_x, l3_y, l3_z)
# file_name = 'l3.h5'
# with h5py.File(targets_dir_path / file_name, 'w') as hf:
#     hf.create_dataset("dataset_1", data=data)
# file_stats = os.stat(targets_dir_path / file_name)
# filesize_l3 = file_stats.st_size
# os.remove(targets_dir_path / file_name)
# print(f'L3: {filesize_l3 / (1024 * 1024 * 1024):.1f} GB')
print('------------------')
print(f'{count_simulated_targets} Targets will be simulated. Let\'s hunt some terrestrial planets')

############## Prepare the directories
for data_layer in data_layers:
    data_layer_dir = DATA_PATH / data_layer
    data_layer_dir.mkdir(exist_ok=True)

    for year in years:
        year_dir = data_layer_dir / str(year)
        year_dir.mkdir(exist_ok=True)

        for quarter in quarters:
            quarter_dir = year_dir / quarter
            quarter_dir.mkdir(exist_ok=True)

            for targets_dir in range(0, max_target_dir, 10000):
                # Creation of target directories with padded with leading zeros
                targets_dir_name = f"{targets_dir:06d}" 
                targets_dir_path = quarter_dir / targets_dir_name
                targets_dir_path.mkdir(exist_ok=True)

                ########## Generating the test data
                if data_layer == 'l1':
                    start_time_l1 = time.time()
                    print(f"Now Generating L1 FITS-Data ({(filesize_l1_day / 1024):.1f} kB per Day, {filesize_l1_90_day_stitch / (1024 * 1024):.1f} MB per {count_simulated_days}-Day-Stitch) for {quarter} of {year}/{max(years)}.")
                    for target in range(0, count_simulated_targets):
                        start_time = time.time()
                        datasets_l1_day = 0
                        datasets_l1_stitch = 0
                        duration_l1_day_once = 0
                        duration_l1_90_days_once = 0

                        # Creation of single files per day
                        for day in range(0, count_simulated_days):
                            data = np.random.random((l1_x, l1_y))
                            fits_data = fits.PrimaryHDU(data)
                            file_name = f'{target:06d}_{day+1}.fits'
                            fits_data.writeto(targets_dir_path / file_name, overwrite=True)
                            datasets_l1_day += 1
                        end_time = time.time()
                        duration_l1_90_days = end_time - start_time
                        duration_l1_days += duration_l1_90_days
                        duration_l1_day_once = duration_l1_90_days

                        # Createion of the 90-Day-stitch
                        start_time = time.time()
                        data = np.random.random((l1_x, l1_y * count_simulated_days))
                        fits_data = fits.PrimaryHDU(data)
                        file_name = f'{target:06d}_stitched.fits'
                        fits_data.writeto(targets_dir_path / file_name, overwrite=True)
                        datasets_l1_stitch += 1
                        end_time = time.time()
                        duration_l1_90_day_stitch += end_time - start_time
                        
                        print(f"Target {target:06d}: {count_simulated_days} days + 1 stitched L1 sets have been created for {quarter} of {year}.")
                    end_time_l1 = time.time()
                    duration_l1 = end_time_l1 - start_time_l1
                    print(f'Generating L1-Data for {quarter} of {year} took {duration_l1:.4f} seconds.')
                    print(f'Generating L1-Day-Data for {quarter} of {year} took {duration_l1_days:.4f} seconds ({datasets_l1_day} Datasets).')
                    print(f'Generating L1-90-Day-Stitch for {quarter} of {year} took {duration_l1_90_day_stitch:.4f} seconds ({datasets_l1_stitch} Datasets).\n')
                    print(f'{datasets_l1_day} L1-Day-Datasets of {(filesize_l1_day / 1024):.1f} kB resulted in {(filesize_l1_day / 1024 * datasets_l1_day)/duration_l1_day_once:.4f} MB/s')
                          
                elif data_layer == 'l2':
                    print(f"Generating L2 HDF5-Data ({(filesize_l2 / (1024 * 1024 * 1024)):.4} GB per target) for {quarter} of {year}/{max(years)}.")
                    for target in range(0, count_simulated_targets):
                        start_time_l2 = time.time()
                        data = np.random.rand(l2_x, l2_y)
                        file_name = f'{target:06d}_data.h5'
                        
                        with h5py.File(targets_dir_path / file_name, 'w') as hf:
                            hf.create_dataset(f"Target_{target:06d}_dataset_{data_layer}_{year}_{quarter}", data=data)
                        end_time_l2 = time.time()
                        duration_l2 = end_time_l2 - start_time_l2
                        print(f"Target {target:06d}: L2 set has been created for {quarter} of {year} with {(filesize_l2 / (1024 * 1024)) / duration_l2:.4} MB/s').")
                  
                elif data_layer == 'l3':
                    start_time_l3 = time.time()
                    print(f"Generating L3 HDF5-Data ({(filesize_l3 / (1024 * 1024 * 1024)):.4} GB per target) for {quarter} of {year}/{max(years)}.")
                    for target in range(0, count_simulated_targets):
                        data = np.random.rand(l3_x, l3_y, l3_z)
                        file_name = f'{target:06d}_data.h5'
                        with h5py.File(targets_dir_path / file_name, 'w') as hf:
                            hf.create_dataset("dataset_1", data=data)

                        print(f"Target {target:06d}: L3 set has been created for {quarter} of {year}/{max(years)}.")
                        end_time_l3 = time.time()
                        duration_l3 = end_time_l3 - start_time_l3
                        print(f"Target {target:06d}: L3 set has been created for {quarter} of {year} with {(filesize_l3 / (1024 * 1024)) / duration_l3:.4} MB/s').")
                else:
                    print("ERROR.")
        print(f"--- Year {year} done! ---")
    print(f"------- Layer {data_layer} done! Total Datasets: {datasets_l1_day}')-------")
print("Done.")
