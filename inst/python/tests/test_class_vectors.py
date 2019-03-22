from unittest import TestCase
import os
import pandas as pd

from restools import binary_parser
from restools.binary_parser import is_valid_vector
from restools.postprocess import ecl_vectors


class TestReadVectors(TestCase):
    @classmethod
    def setUpClass(cls):
        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        cls.parser = binary_parser.EclBinaryParser(unsmry_file)
        cls.vectors = cls.parser.read_vectors()
        os.chdir(cur_dir)

    @classmethod
    def tearDownClass(cls):
        pass
        # cls.well.shutdown()

    def test_shape_vectors_raw(self):
        result = self.vectors.shape
        # print(result)
        self.assertEqual(result, (1611, 5000))

    def test_get_vector_shape_function(self):
        # print(self.vectors.get_vectors_shape())
        result = self.parser.get_vectors_shape()
        # print(result)
        self.assertEqual(result, (1611, 5000))

    def test_get_vector_names_raw(self):
        expected = ecl_vectors.ecl_vectors
        result = sorted(set(self.vectors.columns.get_level_values(0)))
        print(sorted(result))
        self.assertEqual(result, expected)

    def test_get_vector_names_function(self):
        expected = ecl_vectors.ecl_vectors
        result = self.parser.get_vector_names()
        # print(result)
        self.assertEqual(result, expected)

    def test_is_valid_vector_raw(self):
        # test that a vector name belongs to a list of Eclipse vectors
        valid_vectors = ecl_vectors.ecl_vectors
        vector_name = "FOPR"
        result = vector_name in valid_vectors
        self.assertTrue(result)

    def test_is_not_valid_vector_raw(self):
        # test that a vector name belongs to a list of Eclipse vectors
        valid_vectors = ecl_vectors.ecl_vectors
        vector_name = "FOPRXYZ"
        result = vector_name in valid_vectors
        self.assertFalse(result)

    def test_is_valid_vector_stat_function(self):
        # test the static function is_valid_vector
        a_vector = "FOPR"
        result = binary_parser.is_valid_vector(a_vector)
        # print(result)
        self.assertTrue(result)

    def test_get_vector_column_raw(self):
        vector_name = "FOPR"
        if is_valid_vector(vector_name):
            fopr = self.vectors[[vector_name]]  # get a vector

            fopr_us = fopr.unstack()            # unstack the mulitiindex df
            fopr_us_ri = fopr_us.reset_index()  # reset the index of the df

            # print(type(fopr))
            # print(type(fopr_us))
            # print(type(fopr_us_ri))

            self.assertIsInstance(fopr, pd.core.frame.DataFrame)
            self.assertIsInstance(fopr_us, pd.core.series.Series)
            self.assertIsInstance(fopr_us_ri, pd.core.frame.DataFrame)

            # last of the dataframe column MINISTEP
            result_us_ri = fopr_us_ri.tail(1)   # last row
            result_ministep_last = result_us_ri[["MINISTEP"]]  # select column

            # the value of the last row
            result_ministep_last_value = result_ministep_last.iloc[0, 0]
            # print(result_ministep_last_value)
            self.assertEqual(result_ministep_last_value, 1610)

            # it should be of class pandas.DataFrame
            self.assertIsInstance(result_ministep_last, pd.core.frame.DataFrame)
            # self.assertEqual(result_ministep_last, 1610)

            result_columns = fopr_us_ri.columns.to_list()
            print(result_columns)  # print df columns
            expected_columns = ['Vector', 'Well/Group', 'Cell/Region', 'Units', 'MINISTEP', 0]
            self.assertListEqual(result_columns, expected_columns)

            result_2030 = fopr_us_ri[0][20:30].sum()
            # print(result_2030)  # select column 0, the values
            self.assertAlmostEqual(result_2030, 24022.31665, places=4)

    def test_get_vector_column_function(self):
        # print(self.parser.get_vector_column("FOPR"))
        fopr_column = self.parser.get_vector_column("FOPR")
        # print(fopr_column)
        # print(fopr_column.columns)
        # print(type(fopr_column))

        # test the type of the class: it is a dataframe, not a series
        self.assertEqual(type(fopr_column), pd.core.frame.DataFrame)

        # this is to test a series
        # print(fopr_column.iloc[:])
        # result = fopr_column.iloc[:].sum()  # 5412071.278167725
        # self.assertAlmostEqual(result, 5412071, places=0)  # field oil production rate

        result = fopr_column[0].sum()  # 5412071.278167725
        self.assertAlmostEqual(result, 5412071, places=0)  # field oil production rate

        fwpr_column = self.parser.get_vector_column("FWPR")
        result = fwpr_column[0].sum()  # 5412071.278167725
        self.assertAlmostEqual(result, 7732239.255, places=3)

        fopt_column = self.parser.get_vector_column("FOPT")
        result = fopt_column[0].tail(1).iloc[0]
        # print(result)
        self.assertEqual(result, 9980819.0)             # field oil production total

        fwpt_column = self.parser.get_vector_column("FWPT")
        result = fwpt_column[0].tail(1).iloc[0]
        # print(result)
        self.assertEqual(result, 15543996.0)              # cumulative water

        # FWCT: Field Watercut
        fwct_column = self.parser.get_vector_column("FWCT")
        result = fwct_column[0].mean()
        # print(result)
        self.assertAlmostEqual(result, 0.550, places=3)  # average field watercut

        # FPR: Field Average Pressure
        fpr_column = self.parser.get_vector_column("FPR")
        result = fpr_column[0]
        # print(result.max())
        # print(result.min())
        self.assertAlmostEqual(result.min(), 280, places=0)   # average field pressure
        self.assertAlmostEqual(result.mean(), 332, places=0)   # average field pressure
        self.assertAlmostEqual(result.max(), 357.6, places=1)  # average field pressure

        fgor_column = self.parser.get_vector_column("FGOR")
        result = fgor_column[0]
        # print(result.max())
        # print(result.mean())
        # print(result.min())
        self.assertAlmostEqual(result.max(), 159, places=0)
        self.assertAlmostEqual(result.mean(), 139, places=0)
        self.assertAlmostEqual(result.min(), 0, places=0)  # average field GOR




