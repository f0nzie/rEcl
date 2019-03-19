import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import re
from mmap import mmap
from struct import unpack_from
from collections import namedtuple, defaultdict
import warnings


# This is for running in a notebook with %run magic
from postprocess.static_mnemonics import static_props
from postprocess.dynamic_mnemonics import dynamic_props

import logging
logger = logging.getLogger()
f_handler = logging.FileHandler(filename='read_vectors.log', mode='w')
formatter = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')
f_handler.setFormatter(formatter)
logger.addHandler(f_handler)
logger.setLevel(logging.INFO)

type_dict = {b'INTE': 'i', b'CHAR': '8s', b'REAL': 'f',
             b'DOUB': 'd', b'LOGI': '4s', b'MESS': '?'}

ecl_extensions = ['.DATA', '.DBG', '.ECLEND', '.EGRID', '.FEGRID', '.FGRID',
                  '.FINIT', '.FINSPEC', '.FRFT', '.FRSSPEC', '.FSMSPEC',
                  '.FUNRST', '.FUNSMRY', '.GRID', '.INIT', '.INSPEC', '.MSG',
                  '.PRT', '.RFT', '.RSM', '.RSSPEC', '.SMSPEC', '.UNRST',
                  '.UNSMRY', '.dbprtx']


def byte2str(x):
    if isinstance(x, (list, tuple, np.ndarray)):
        return list(map(byte2str, x))
    else:
        return str(x)[2:-1].strip()


def str2byte(x):
    if isinstance(x, (list, tuple, np.ndarray)):
        return list(map(str2byte, x))
    else:
        return bytes(x.ljust(8).upper(), 'utf-8')


def filter_fakes(filename, ext, loc, target_size, fmt='>f', excl=np.inf):
    """
    Reads binary data from Eclipse output and filters fake values
    (the ones outside of actual property/vector ranges)
    that Eclipse inserts at certain positions
    Returns good NumPy array, ready for further work
    """
    with open(filename + ext, 'rb') as f:
        n_sieved = 0  # Number of fake values, initially zero
        tol = 1e-32
        array = np.array([])
        lengths = [0, 1]
        while len(array)<target_size and lengths[-1] != lengths[-2]:
            f.seek(loc+24)
            array = np.fromfile(f, dtype=fmt, count=target_size+n_sieved)
            if fmt == 'S8':  # For read_vectors
                condition = np.array([False if _.startswith('\\') else True
                                      for _ in byte2str(array)])
                array = array[condition]
            elif fmt == '>i' and ext == '.SMSPEC':
                array = array[((np.abs(array) >= tol) | (array == 0))
                              & (np.abs(array) != 4000)
                              & (np.abs(array) != 2980)]
                # No idea why these values are fakes, it maybe unsafe as there
                # may be legitimate nums with these values
            else:
                array = array[((np.abs(array) >= tol)
                               | (array == 0))
                              & (np.abs(array) < excl)]
            n_sieved += target_size - len(array)
            lengths.append(len(array))
    return array


class EclArray(object):
    """
    General class to hold Eclipse array
    """
    def __init__(self, filename, offset=None, keyword=None, with_fakes=True):
        self.filename = filename
        if ((offset is None and keyword is None) or
            (offset is not None and keyword is not None)):
            raise ValueError('Either offset or keyword must be specified')
        # First read file into buffer
        with open(filename, 'rb') as f:
            buff = mmap(f.fileno(), 0, access=1)
        if offset is None:
            offset = next(_.start() for _ in re.finditer(str2byte(keyword), buff))
        self.header = unpack_from('>8si4s', buff, offset)
        self.keyword, self.number, self.typ = self.header
        fmt = '>' + type_dict[self.typ]
        excl = np.inf
        if self.typ == b'INTE':
            excl = 2500
        elif self.typ == b'CHAR':  # For read_vectors to filter fake keywords, wgnames, and units
            fmt = 'S8'
        if with_fakes:
            self.array = filter_fakes(os.path.splitext(filename)[0],
                                      os.path.splitext(filename)[1],
                                      offset, self.number,
                                      fmt=fmt, excl=excl)
        else:
            self.array = np.array(unpack_from('>' + self.number * type_dict[self.typ],
                                              buff, offset + 24))


class EclBinaryParser(object):
    """
    Class for working with Eclipse binary files.
    As an argument takes filename with or without extension.
    """""

    def __init__(self, filename):
        """
        Truncates file extension if filename is provided with one
        """
        if (isinstance(os.path.splitext(filename), tuple) and
            os.path.splitext(filename)[1] in ecl_extensions):
            self.filename = os.path.splitext(filename)[0]
        else:
            self.filename = filename

    def _read_all_arrays(self, ext, keyword, with_fakes):
        """
        Reads all arrays from file with given extension and
        collects them into a list of arrays
        """
        all_arrays = []
        with open('{}.{}'.format(self.filename, ext), 'rb') as f:
            buff = mmap(f.fileno(), 0, access=1)
        keyword_locs = [_.start() for _ in re.finditer(str2byte(keyword), buff)]
        for keyword_loc in keyword_locs:
            all_arrays.append(EclArray('{}.{}'.format(self.filename, ext),
                                       offset=keyword_loc, with_fakes=with_fakes).array)
        return all_arrays

    def _read_all_names(self, ext):
        return self._read_all_arrays(ext, 'NAME', False)

    def _read_all_types(self, ext):
        return self._read_all_arrays(ext, 'TYPE', False)

    def _read_all_pointers(self, ext):
        return self._read_all_arrays(ext, 'POINTER', False)

    def _get_static_pointers(self):
        static_names = self._read_all_names('INSPEC')
        static_pointers = self._read_all_pointers('INSPEC')
        for _, (names, pointers) in enumerate(zip(static_names, static_pointers)):
            df0 = pd.DataFrame(pointers, index=names, columns=[_])
            if _ == 0:
                df = df0
            else:
                df = df.join(df0, how='outer')
            df = df[~df.index.duplicated(keep='first')]
        df.fillna('-9999', inplace=True)
        df = df.astype('int32').T.max()
        return df

    def _get_dynamic_pointers(self):
        dynamic_names = self._read_all_names('RSSPEC')
        dynamic_pointers = self._read_all_pointers('RSSPEC')
        for _, (names, pointers) in enumerate(zip(dynamic_names, dynamic_pointers)):
            df0 = pd.DataFrame(pointers, index=names, columns=[_])
            if _ == 0:
                df = df0
            else:
                df = df.join(df0, how='outer')
            df = df[~df.index.duplicated(keep='first')]
        df.fillna('-9999', inplace=True)
        df = df.astype('int32')
        df.columns = self.get_seqnum_dates().index
        return df

    def _get_all_pointers(self):
        all_pointers = pd.concat([self._get_static_pointers(),
                                  self._get_dynamic_pointers()])
        all_pointers = all_pointers.fillna(method='ffill', axis=1).astype('int32').T
        all_pointers.columns = [byte2str(column) for column in all_pointers.columns]
        all_pointers = self.get_seqnum_dates().join(all_pointers)
        return all_pointers

    def get_dimens(self):
        """
        Parses RSSPEC file and returns model dimensions.
        """
        with open(self.filename + '.RSSPEC', 'rb') as f:
            rsspec = mmap(f.fileno(), 0, access=1)  # Read-only access
        Dimens = namedtuple('DIMENS', 'ni, nj, nk')
        ni, nj, nk = unpack_from('>3i', rsspec, offset=60)
        return Dimens(ni, nj, nk)

    def is_dual(self):
        """
        Checks if model is a dual-porosity model
        """
        if len(EclArray(self.filename + '.INIT', keyword='LOGIHEAD',
                        with_fakes=False).array[14]) != 0:
            return True
        else:
            return False

    def get_actnum(self):
        porv_array = EclArray(self.filename + '.INIT',
                              keyword='PORV', with_fakes=True).array
        return ma.masked_equal(porv_array, 0)

    def get_seqnum_dates(self, condensed=True):
        itimes = self._read_all_arrays('RSSPEC', 'ITIME', False)
        columns = ['SEQNUM', 'DAY', 'MONTH', 'YEAR', 'MINISTEP',
                   'IS_UNIFIED', 'IS_FORMATTED', 'IS_SAVE', 'IS_GRID', 'IS_INIT',
                   'HOUR', 'MINUTE', 'MICROSECOND']
        df = pd.DataFrame(itimes, columns=columns).set_index('SEQNUM')
        if condensed:
            df['DATETIME'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY',
                                                'HOUR', 'MINUTE', 'MICROSECOND']],
                                            format='%Y-%m-%d %H:%M:%S:%f')
            df = pd.DataFrame(df['DATETIME'])
        return df

    def read_prop_array(self, prop, date=None):
        warnings.filterwarnings('ignore')
        seqnum_dates = self.get_seqnum_dates()
        ni, nj, nk = self.get_dimens()
        if prop.upper() not in self._get_all_pointers().columns:
            raise ValueError('There is no {} property'.format(prop))
        if date is None:
            # Take the first date
            date = seqnum_dates.iloc[0, -1]
        if date not in seqnum_dates['DATETIME']:
            raise ValueError('There is no {} date among available restart dates'.format(date))
        seqnum = seqnum_dates[seqnum_dates['DATETIME']==date].index[0]
        if prop in static_props:
            df = pd.DataFrame(self._get_static_pointers())
            ext = '.INIT'
        else:
            df = self._get_dynamic_pointers()
            ext = '.UNRST'
        pointer = df.loc[str2byte(prop), seqnum] + 4
        if pointer > 0:
            prop_array = EclArray(self.filename + ext,
                                  offset=pointer, with_fakes=True).array
            # Map values from INIT/UNRST to actnum array,
            # filling inactive cells with NaN's
            temp_array = self.get_actnum()
            temp_array[temp_array==0] = np.nan
            temp_array[temp_array>0] = prop_array
            # Reshape values array to Eclipse grid dimensions
            # Order of coordinates is reversed because
            # Eclipse counts first by I, then by J, then by K
            # Transpose prop_array to get to Eclipse format (i-1,j-1,k-1)
            return np.reshape(temp_array, (nk, nj, ni)).T
        else:
            print('No {0} value at {1}. Assuming zero for plotting \
                  '. format(prop, date))
            return np.zeros((nk, nj, ni)).T

    def read_prop_time(self, prop, i, j, k):
        dates = self._get_all_pointers()['DATETIME']
        values = [self.read_prop_array(prop, date)[i-1, j-1, k-1] for date in dates]
        return pd.DataFrame(values, index=dates,
                            columns=['{}@({}, {}, {})'.format(prop, i, j, k)])

    def read_vectors(self):
        smspec = self.filename + '.SMSPEC'
        nlist, ni, nj, nk = EclArray(smspec, keyword='DIMENS',
                                     with_fakes=False).array[:4]
        logging.debug('nlist: {}, ni: {}, nj: {}, nk: {}'.format(nlist, ni, nj,
                                                                 nk))
        keywords = byte2str(EclArray(smspec, keyword='KEYWORDS', with_fakes=True).array)
        logging.debug('keywords: {}'.format(keywords))
        wgnames = byte2str(EclArray(smspec, keyword='WGNAMES', with_fakes=True).array)
        logging.debug('wgnames: {}'.format(wgnames))
        nums = EclArray(smspec, keyword='NUMS', with_fakes=True).array
        logging.debug('nums: {}'.format(nums))
        units = byte2str(EclArray(smspec, keyword='UNITS', with_fakes=True).array)
        logging.debug('units: {}'.format(units))
        logging.debug('LENGTHS')
        logging.debug('-------')
        logging.debug('keywords: {}'.format(len(keywords)))
        logging.debug('wgnames: {}'.format(len(wgnames)))
        logging.debug('nums: {}'.format(len(nums)))
        logging.debug('units: {}'.format(len(units)))
        logging.debug('ZIPS')
        logging.debug('-------')
        for i in zip(keywords, wgnames, nums, units):
            logging.warning(i)
        new_nums = []
        for keyword, num in zip(keywords, nums):
            if (keyword.startswith('C') or keyword.startswith('B')) and num > 0:
                k = int((num - 1)/(ni*nj) - 0.00001) + 1
                j = int((num - (k - 1)*ni*nj)/ni - 0.00001) + 1
                i = num - (j - 1)*ni - (k - 1)*ni*nj
                num = str('({0}, {1}, {2})'.format(i, j, k))
            else:
                num = str(num)  # Convert NUMs to strings for subsequent plotting
            new_nums.append(num)
        nums = new_nums
        logging.debug('NUMS CONVERTED')
        logging.debug('-------')
        for i in nums:
            logging.debug(i)
        params = self._read_all_arrays('UNSMRY', 'PARAMS', True)
        logging.warning(params)
        headers = pd.MultiIndex.from_tuples(
                                    list(zip(*[keywords, wgnames, nums, units])),
                                    names=['Vector', 'Well/Group', 'Cell/Region', 'Units'])
        df = pd.DataFrame(params, columns=headers).sort_index(axis=1)
        df.index.name = 'MINISTEP'
        return df
