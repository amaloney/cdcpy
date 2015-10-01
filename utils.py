# -*- coding: utf-8 -*-

"""
"""

import datetime
import urlparse
import urllib
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

# TODO: Put these in a config file.
_valid_sources = {'ili': 'ILINet',
                  'ilinet': 'ILINet',
                  'who': 'WHO_NREVSS',
                  'nrevss': 'WHO_NREVSS'}
_valid_source_keys = list(set(_valid_sources.values()))
_valid_sources_string = ', '.join(map(str, _valid_source_keys))
_valid_seasons_start = 37
_start_of_data_collection = 1997
_valid_regions = {'hhs': 1,
                  'hhs region': 1,
                  'census': 2,
                  'national': 3}


def check_data_sources(data_sources):
    r"""Checks if the supplied data source is valid. If not, then it raises
    an error.

    Parameters
    ----------
    data_sources : string
        Influenza data source supplied by FluView.

    Returns
    -------
    data_source_header : dictionary
        The correctly formatted data source header for FluView.

    """
    valid = _valid_sources.keys()
    header = []
    bad_sources = []
    if not isinstance(data_sources, (str, list)):
        msg = 'The data source must be a string or a list of strings.'
        raise ValueError(msg)
    if isinstance(data_sources, str):
        data_sources = [data_sources]
    for data_source in data_sources:
        if data_source.lower() not in valid:
            bad_sources.append(data_source)
        if data_source.lower() in valid:
            header.append(data_source)
    if bad_sources:
        msg = ('%s is not a valid data source.\n'
               '            Valid sources are: %s' %
               (bad_sources, _valid_sources_string))
        raise ValueError(msg)
    else:
        header_string = ','.join(map(lambda x: _valid_sources[x], header))
        data_source_header = {'DataSources': header_string}
        return data_source_header


def most_recent_season():
    r"""Returns the integer corresponding to the current season list maximum
    in FluView.

    Returns
    -------
    season : integer
        The integer representation of the current flu season as defined by
        FluView.

    """
    iso_date = datetime.datetime.now().isocalendar()
    current_year = iso_date[0]
    current_week = iso_date[1]
    msg = 'ISO data: %s' % str(iso_date)
    logger.debug(msg)
    season = 0
    if current_week < 40:
        season = current_year - _start_of_data_collection - 1 +\
                 _valid_seasons_start
    if current_week >= 40:
        season = current_year - _start_of_data_collection +\
                 _valid_seasons_start
    if season == 0:
        msg = 'There was a problem calculating the current season integer.'
        raise ValueError(msg)
    else:
        return season


def check_seasons(seasons):
    r"""Checks if the given season is a valid number.

    Parameters
    ----------
    seasons : integer
        The start of available data begins with season 37.

    Returns
    -------
    seasons_header : dictionary
        The correctly formatted seasons header for FluView.

    """
    header = []
    bad_seasons = []
    this_season = most_recent_season()
    if seasons == 'all':
        header_string = ','.join(map(str, range(37, this_season + 1)))
        seasons_header = {'SeasonsList': header_string}
        return seasons_header
    if not isinstance(seasons, (int, list)):
        msg = 'The season must be an integer or a list of integers.'
        raise ValueError(msg)
    if isinstance(seasons, int):
        seasons = [seasons]
    for season in seasons:
        if not isinstance(season, int):
            bad_seasons.append(season)
        if season < _valid_seasons_start:
            bad_seasons.append(season)
        else:
            header.append(season)
    if bad_seasons:
        msg = ('%s is not a valid season.\n'
               '            Valid seasons begin with: %s and must be integers.'
               % (bad_seasons, _valid_seasons_start))
        raise ValueError(msg)
    else:
        header_string = ','.join([str(x) for x in header if x <= this_season])
        seasons_header = {'SeasonsList': header_string}
        return seasons_header


def check_region(region):
    r"""Checks if the supplied region is valid. If not, then it raises
    an error.

    Parameters
    ----------
     region : string OR integer
        The region of interest for the requested data.
            * HHS Regions = 1
            * Census = 2
            * National = 3

    Returns
    -------
    region_header : dictionary
        The correctly formatted region header for FluView.

    """
    if not isinstance(region, (int, str)):
        msg = 'The region must be a string or an integer.'
        raise ValueError(msg)
    # If the given region is given as an integer in string form, convert it.
    try:
        region = int(float(region))
    except:
        region = region
    if isinstance(region, int):
        if region < 1 or region > 3:
            msg = ('Valid values for regions are 1 = HHS, 2 = Census, '
                   '3 = National.')
            raise ValueError(msg)
        else:
            header_string = region
            region_header = {'RegionID': header_string}
            return region_header
    if isinstance(region, str):
        if region.lower() not in _valid_regions.keys():
            msg = ('%s is not a valid region. '
                   'Valid values for regions are 1 = HHS, 2 = Census, '
                   '3 = National.' % region)
            raise ValueError(msg)
        else:
            header_string = _valid_regions[region.lower()]
            region_header = {'RegionID': header_string}
            return region_header


def check_sub_regions(region, sub_regions):
    r"""If the supplied region has subregion categories, this will check if
    they are valid and will return a properly formatted header for the
    FluView subregion.

    Parameters
    ----------
    region : dictionary
        The correctly formatted header information for the FluView region.
    subregion : string, integer OR list
        The subregion of interest.

    """
    region = region['RegionID']
    subregions = set()
    bad_subregions = set()
    valid_hhs_regions = range(1, 11)
    valid_census_regions = {'new england': 1,
                            'mid-atlantic': 2,
                            'east north central': 3,
                            'west north central': 4,
                            'south atlantic': 5,
                            'east south central': 6,
                            'west south central': 7,
                            'mountain': 8,
                            'pacific': 9}
    if not isinstance(sub_regions, (int, float, str, list)):
        msg = ('The subregions must be a string, integer, or a list of '
               'stings or integers.')
        raise ValueError(msg)
    if isinstance(sub_regions, int):
        if sub_regions < 1:
            msg = 'Valid subregions are positive integers.'
            raise ValueError(msg)
        subregions.add(sub_regions)
    if isinstance(sub_regions, float):
        if sub_regions < 1:
            msg = 'Valid subregions are positive integers.'
            raise ValueError(msg)
        subregions.add(int(sub_regions))
    if isinstance(sub_regions, str):
        try:
            sub_regions = int(float(sub_regions))
        except:
            sub_regions = sub_regions
        subregions.add(sub_regions)
    if isinstance(sub_regions, list):
        if region == 1:
            for sr in sub_regions:
                try:
                    _sr = int(float(sr))
                    if _sr < max(valid_hhs_regions) and _sr >= 1:
                        subregions.add(_sr)
                    else:
                        bad_subregions.add(_sr)
                except:
                    msg = ('The HHS Regions accept only integers as inputs.\n'
                           '            "%s" is not a valid input.' % sr)
                    raise ValueError(msg)
        if region == 2:
            for sr in sub_regions:
                try:
                    _sr = int(float(sr))
                    if _sr < max(valid_census_regions.values()) and _sr >= 1:
                        subregions.add(_sr)
                    else:
                        bad_subregions.add(_sr)
                except:
                    if sr.lower() in valid_census_regions.keys():
                        subregions.add(valid_census_regions[sr])
                    else:
                        bad_subregions.add(sr)
    if bad_subregions:
        msg = ('%s is not a valid subregion.\n'
               '            Valid subregions depend on the given region.\n'
               '            Region 1 (HHS Region): %s\n'
               '            Region 2 (Census): %s.'
               % (bad_subregions, valid_hhs_regions,
                  valid_census_regions))
        raise ValueError(msg)
    header_string = ','.join(map(str, subregions))
    subregion_header = {'SubRegionsList': header_string}
    return subregion_header
