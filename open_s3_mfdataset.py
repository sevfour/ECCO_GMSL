import s3fs
import xarray as xr
import numpy as np

def open_s3_mfdataset(s3_subdir, file_index = -1, s3_bucket='s3://ecco-processed-data/SASSIE/N1_test/HH/NETCDF'):
    """
    Marie Zahn - October 2024
    
    Function that opens all netcdfs in 's3_subdir' from the ECCO s3 bucket that does NOT require specific credentials (e.g., SASSIE s3 bucket)

    Args:
    s3_subdir: directory that contains netCDF files that you would like to open
    file_index: specify "-1" to open all files in 's3_subdir' or provide an index for an individual file to open
    s3_bucket: s3 bucket path that contains 's3_subdir'

    returns: ds

    Examples:
    salt_snaps = open_s3_mfdataset('SALT_SNAP', file_index = -1, s3_bucket='s3://ecco-processed-data/SASSIE/N1_test/HH/NETCDF') #For all files within 'SALT_SNAP' directory
    salt_snaps = open_s3_mfdataset('SALT_SNAP', file_index = 0, s3_bucket='s3://ecco-processed-data/SASSIE/N1_test/HH/NETCDF') #For only first file within 'SALT_SNAP' directory
    """
    # initialize s3 filesystem
    s3 = s3fs.S3FileSystem(anon=False)

    # get list of netCDF files
    file_list = s3.glob(f'{s3_bucket}/{data_variable}/*.nc')

    # create urls from s3 bucket path to be used for opening files
    file_list_url = []
    for i in range(len(file_list)):
        file_list_url.append('s3://' + file_list[i])
    
    if file_index == -1: # open all files
        # iterate through remote files to create a fileset
        fileset = [s3.open(file) for file in file_list_url]
        
        # open on local ec2
        ds = xr.open_mfdataset(fileset)
    else:
        # open on local ec2
        file_list_url_sort = np.sort(file_list_url)
        ds = xr.open_dataset(s3.open(file_list_url_sort[file_index]))
        
    return ds