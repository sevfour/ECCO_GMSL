import numpy as np
import os, glob
import netCDF4 as nc
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import time
import sys
from pathlib import Path 
from pyresample import kd_tree, geometry, utils
import xarray as xr
import myDate

# input directory name for alongtrack
# at_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/ECCO_V4r4_alongtrack_output_nosicapplied/')
at_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/ECCO_V4r4_alongtrack_output_randomnoise_nosicapplied/')
# at_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/ECCO_V4r4_alongtrack_output_missingdata_nosicapplied/')
# at_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/ECCO_V4r4_alongtrack_output_orbiterror_2cm_nosicapplied/')
# at_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/ECCO_V4r4_alongtrack_output_3errors_2cm_nosicapplied/')

# output directory name for grids
# grids_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/gridding_output_nosicapplied/')
grids_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/gridding_output_randomnoise_nosicapplied/')
# grids_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/gridding_output_missingdata_nosicapplied/')
# grids_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/gridding_output_orbiterror_2cm_nosicapplied/')
# grids_file_dir = Path('/home/jpluser/ECCO_GMSL/Data/gridding_output_3errors_2cm_nosicapplied/')

# other directories
main_dir = Path('/home/jpluser/ECCO_GMSL/')
data_dir = Path('/home/jpluser/ECCO_GMSL/Data/')

# Parameter definition
roi=600e3
sig=100e3
nb=500


####################################### BASIN MASK ###################################################

# load the basin mask for the grid we are using
nf=nc.Dataset(os.path.join(data_dir, 'new_basin_mask.nc'),'r')
longrid=np.array(nf['lon'])
latgrid=np.array(nf['lat'])
bmask=np.array(nf['basinmask'])
longrid=longrid[1:-1:3]
latgrid=latgrid[1:-1:3]
bmask=bmask[1:-1:3,1:-1:3]
nf.close()

# change longitudes to +/- 180
ind=np.where(longrid>180)
ind1=np.where(longrid<=180)
longrid[ind] = longrid[ind]-360
longrid=np.hstack((longrid[ind],longrid[ind1]))
bmask=np.hstack((bmask[:,ind].squeeze(),bmask[:,ind1].squeeze()))

LOgrid,LAgrid=np.meshgrid(longrid,latgrid)

# make a "grid" for this basin mask grid
bmask_grid_def = geometry.GridDefinition(lons=LOgrid, lats=LAgrid)

# read in connection table 
# this tells us which basin numbers are connected
file=open(os.path.join(data_dir, 'basin_connection_table.txt'),'r')
lines=file.read().splitlines()
fid=np.zeros(len(lines),dtype='int16')
flist=[]
for i in range(len(fid)):
    fid[i]=np.int16(lines[i].split(':')[0])
    flist.append(np.int16(lines[i].split(':')[1].split(',')))
file.close() 



####################################### GRIDS FROM SYNTHETIC ECCO ALONGTRACK ################################################### 

time_fiction=range(myDate.date2jj(1992,9,23),myDate.date2jj(2017,12,31)+11)

# loop over each 10-day cycle
for j in np.arange(0,len(time_fiction)-10,10):
    [year,month,day]=myDate.jj2date(time_fiction[j+4])
    fileout=str(grids_file_dir) + '/SSHA_gridded_'+str(year)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)+'.nc'
    print('creating grid '+fileout)
    
    lat=[]
    lon=[]
    ssh=[]
    for i in range(0,10):
        [yy,mm,dd]=myDate.jj2date(time_fiction[j+i])
        if len(glob.glob(os.path.join(at_file_dir, 'ECCO_V4r4_alongtrack_SSH_'+str(yy)+'-'+str(mm).zfill(2)+'-'+str(dd).zfill(2)+'*.nc')))>0:
            file=glob.glob(os.path.join(at_file_dir, 'ECCO_V4r4_alongtrack_SSH_'+str(yy)+'-'+str(mm).zfill(2)+'-'+str(dd).zfill(2)+'*.nc'))[0]
            xds = xr.open_dataset(file)     
            lon=np.concatenate((lon,np.array(xds['lon'])))
            lat=np.concatenate((lat,np.array(xds['lat'])))
            ssh=np.concatenate((ssh,np.array(xds['SSH_at_xy'])))
        else:
            print('no file on: '+str(yy)+str(mm).zfill(2)+str(dd).zfill(2))
    
    # change longitudes to +/- 180
    ii=np.where(lon>180)
    lon[ii]=lon[ii]-360
    
    # create bflag that tells us which basin is in each ssh alongtrack (interpolation of swath on basin grid)
    lon,lat = utils.check_and_wrap(lon,lat)
    ssh_swath_def = geometry.SwathDefinition(lons=lon, lats=lat)
    bflag=kd_tree.resample_nearest(bmask_grid_def,bmask,ssh_swath_def,radius_of_influence=200000,fill_value = 0)
    
    # make grid 1 piece at a time, basin by basin
    tmpmap=np.zeros(np.shape(LOgrid))*np.nan
    counts=np.zeros(np.shape(LOgrid))*np.nan
    for i in range(len(fid)):
        # get grid points for this basin number
        ll=np.where(bmask==fid[i])
        if np.shape(ll)[1]>0:
            ii=np.where((np.isfinite(ssh)&np.isin(bflag,flist[i])))[0]
            if len(ii)>nb:
                # make a "swath" for this set of output grid points
                grid_def=geometry.SwathDefinition(lons=LOgrid[ll],lats=LAgrid[ll])
                # make a "swath" for this set of along track data
                alongtrack_def=geometry.SwathDefinition(lons=lon[ii], lats=lat[ii])
                # use pyresample to do gridding
                tmpmap[ll], _, counts[ll]=kd_tree.resample_gauss(alongtrack_def,ssh[ii],grid_def,roi,sigmas=sig,neighbours=nb,with_uncert=True,fill_value=np.nan)

    ds = xr.Dataset({'SSHA':(('latitude','longitude'), tmpmap),
                    'counts':(('latitude','longitude'), counts)},
                coords={'latitude': latgrid,'longitude':longrid,'time':datetime(year, month, day)})
    ds['time'].attrs['long_name'] = 'center of 10-day cycle'
    
    ds['SSHA'].attrs['long_name'] = 'sea surface height anomaly'
    ds['SSHA'].attrs['units'] = 'm'
    ds['SSHA'].attrs['_FillValue'] = np.nan
    ds['SSHA'].attrs['comment'] = "Data gridded to 0.5 degree lat lon grid using simple-gridder and basin mask"
    
    ds['counts'].attrs['long_name'] = 'number of data values used in weighting each element in SSHA'
    ds['counts'].attrs['_FillValue'] = np.nan
    ds['counts'].attrs['comment'] = "Returned from pyresample resample_gauss function"
    
    ds['latitude'].attrs['long_name'] = 'latitude'
    ds['latitude'].attrs['_FillValue'] = np.nan
    ds['latitude'].attrs['units'] = 'degrees_east'
    
    ds['longitude'].attrs['long_name'] = 'longitude'
    ds['longitude'].attrs['_FillValue'] = np.nan
    ds['longitude'].attrs['units'] = 'degrees_north'
    ds.to_netcdf(fileout)
