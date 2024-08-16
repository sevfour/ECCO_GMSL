Steps:

- 01-ECCO_V4r4_SSH_mean: Compute mean SSH 1992-2017 from ECCO

- 02-Create_Alongtrack_sample_file: Create nc sample files (1 full cycle, all cycles including missing data, all cycles with no missing data and orbit error param, all cycles with missing data and orbit error param). Output: Data/ and Data/errors/

- Different orbit error std for Create_Alongtrack_sample_file

- 03-ECCO_V4r4_SSH_to_alongtrack_allyears: Create 1 netCDF file per day (ECCO_V4r4_alongtrack_SSH_<date>.nc) of along track SSH without error or missing data simulated on ECCO. Output: ECCO_V4r4_alongtrack_output

- 04-ECCO_V4r4_SSH_to_alongtrack_allyears_missingdata: Create 1 netCDF file per day (ECCO_V4r4_alongtrack_SSH_<date>_missingdata.nc) of along track SSH with missing data, simulated on ECCO. Output: ECCO_V4r4_alongtrack_output_missingdata

- 05-ECCO_V4r4_SSH_to_alongtrack_allyears_randomnoise: Create 1 netCDF file per day (ECCO_V4r4_alongtrack_SSH_<date>_randomnoise.nc) of along track SSH with random noise, simulated on ECCO. We simply add random noise to the alongtrack array with mu=0, std=3cm (0.03m). Output: ECCO_V4r4_alongtrack_output_randomnoise

- 06-ECCO_V4r4_SSH_to_alongtrack_allyears_orbiterror: Create 1 netCDF file per day (ECCO_V4r4_alongtrack_SSH_<date>_orbiterror.nc) of along track SSH with orbit error, simulated on ECCO (STD error of 2cm can be changed). We add per orbit (~112 min): orbit error = amplitude * sin(2 pi t/T + phase) with amplitude=random.normal(0,0.01,1) (random gaussian distribution mean 0 and std 0.01) and phase=(random nb between 0 and 1)*2*pi. Output: ECCO_V4r4_alongtrack_output_orbiterror.

- 07-ECCO_V4r4_SSH_to_alongtrack_allyears_3errors: Create 1 netCDF file per day (ECCO_V4r4_alongtrack_SSH_<date>_3errors.nc) of along track SSH with missing data, random noise and orbit error, simulated on ECCO. Output: ECCO_V4r4_alongtrack_output_3errors, with other orbit error values too

- Create grids from these along track data by running simple_gridder program after changing config file (conf.yaml): python simple_gridder.py. Output: gridding_output_...

- 08/09/10-GMSL: Create netCDF files with the GMSL time series for along track data from Beckley and ECCO synthetic with no error, random error, missing data, orbit error and 3 errors, as well as GMSL time series computed from synthetic grids and daily ECCO gridded data. Output: GMSL

- 11-GMSL_plots: GMSL plots for different methods global average
