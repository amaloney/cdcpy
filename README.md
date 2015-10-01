# cdcpy
Python module to directly import data from the CDC FluView dashboard
(http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) into an interactive
session.

Currently, the module will import data from FluView and save to a csv file. It
will also save the imported data into a pandas data frame for further analysis.

# Required packages
* requests (http://docs.python-requests.org/en/latest/)
* pandas (http://pandas.pydata.org/)

# Example usage
Navigate to where you downloaded the module and start up iPython.

```python
import cdc
import pandas

# Interactive session with pandas.
ili = cdc.FluView(data_sources='ili', seasons='all', region='census',
                  sub_regions=[1, 2])
df = ili.to_pandas_df()
df.columns

# Saving to a csv file.
ili.save_csv()
```
If you save to a csv file and do not specify a filename or path, then the file
will be saved to the same directory where you started iPython with a timestamp
as the filename.

A few notes about the input parameters:
* data_sources
  * You can collect data specifically from the ILI database or the WHO NREVSS
    from FluView or both. If you want both ILI and WHO data you can modify the
    data_sources variable to be a list such as ['ili', 'who'].
* seasons
  * The seasons variable can also be modified to be a list of season integers
    or a single season of interest, *e.g.* seasons=45 or seasons=[37,49,55].
* region
  * The region parameter can be an integer or a string indicating which region
    of interest to pull data from, *e.g* region='national' or region=3.
* sub_regions
  * If you have chosen the region to be either **census (2)** or **hhs (1)**
    then you can specify a single subregion or a list of subregions to
    collect data on. Valid subregion values are:
    * HHS Regions
      * An integer from [1, 10]
    * Census
      * An integer from [1, 9] or
      * a string from ['new england', 'mid-atlantic', 'east north central',
                       'west north central', 'south atlantic',
                       'east south central', 'west south central', 'mountain',
                       'pacific']
    * Note that if you select the region to be *national*, then there are
      no subregions to collect data on.
