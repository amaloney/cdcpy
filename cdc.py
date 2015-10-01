# -*- coding: utf-8 -*-

"""
"""

import os
from zipfile import ZipFile
from StringIO import StringIO
from datetime import datetime
import logging

import requests
import pandas

import utils

logger = logging.getLogger(__name__)


class FluView(object):

    def __init__(self, data_sources, seasons, region, sub_regions):
        r"""Downloads influenza data from
        http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html
        and returns a pandas dataframe with the requested data.

        Parameters
        ----------
        data_sources : string OR list
            The source for influenza data. Currently there are two options
            given by FluView.
                * ILINet
                * WHO_NREVSS
            Both sources can be queried at the same time if given as a list.
        season : integer OR list OR 'all'
            The influenza season of interest. A range of seasons can be
            collected if given as a list. The maximum integer value for the
            list is calculated and truncated if the given list exceeds this
            value. If a value of 'all' is given, then all the seasons
            available for download will be collected.
        region : string OR integer
            The region of interest for the requested data.
                * HHS Regions = 1
                * Census = 2
                * National = 3
        sub_region : string

        """
        self._url = ('http://gis.cdc.gov/grasp/fluview/'
                     'FluViewPhase2CustomDownload.ashx')
        self.data_sources = utils.check_data_sources(data_sources)
        self.seasons = utils.check_seasons(seasons)
        self.region = utils.check_region(region)
        self.subregions = utils.check_sub_regions(self.region, sub_regions)
        self._header = self._build_headers()

    def _build_headers(self):
        r"""Builds the proper header data to send to FluView.

        Returns
        -------
        headers : dictionary
            A dictionary representation of the headers to send to FluView.

        """
        headers = {}
        headers.update(self.data_sources)
        headers.update(self.seasons)
        headers.update(self.region)
        headers.update(self.subregions)
        return headers

    def _get_data(self, pd=False):
        r"""Acquires data from FluView based on the given parameters in the
        __init__ function.

        Parameters
        ----------
        pd : boolean
            DEFAULT: False
            Determines if the data is to be placed into a pandas dataframe.

        Returns
        -------
        data : list
            Data from FluView converted to a Python list.

        """
        r = requests.post(self._url, self._header)
        compressed_data = ZipFile(StringIO(r.content))
        data = {name: compressed_data.read(name)
                for name in compressed_data.namelist()}
        data = data[data.keys()[0]]
        if pd:
            data = pandas.read_csv(StringIO(data))
            return data
        data = data.split('\n')
        data = [datum for datum in data if datum]
        return data

    def to_pandas_df(self):
        r"""Returns the data from FluView into a pandas dataframe.

        Returns
        -------
        data : pandas.DataFrame
            A pandas DataFrame object.

        Example
        -------
        >>> import pandas
        >>> data_sources = ['ili', 'who']
        >>> seasons = 'all'
        >>> region = 'census'
        >>> sub_regions = [1, 2, 3]
        >>> ili = cdc.FluView(data_sources=data_sources, seasons=seasons,
                              sub_regions=sub_regions)
        >>> df = ili.to_pandas()
        >>> df.columns
        Index([...

        """
        data = self._get_data(pd=True)
        return data

    def save_csv(self, save_path=''):
        r"""Saves the FluView data to a csv file.

        Parameters
        ----------
        save_path : string
            DEFAULT: ''
            The path to save the data to. If no path is given, then the data
            is saved to the same folder where the Python session is. File
            names will then be a timestamp of the pull.

        """
        if not save_path:
            time = datetime.now()
            time = datetime.strftime(time, '%Y-%m-%d_%H:%M:%S')
            filename = time + '.csv'
            save_path = os.path.join(os.path.abspath(os.curdir), filename)
        data = self._get_data()
        with open(save_path, 'wb') as f:
            for line in data:
                f.write(line + '\n')
