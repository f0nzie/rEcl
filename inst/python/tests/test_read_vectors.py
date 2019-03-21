import os
from unittest import TestCase
from restools import binary_parser


class TestReadingVectors(TestCase):

    def test_read_unsmry_file(self):
        unsmry_file = "./volve/VOLVE_2016.UNSMRY"
        parser = binary_parser.EclBinaryParser(unsmry_file)
        self.assertEqual(parser.filename, "./volve/VOLVE_2016")

    def test_read_vectors_shape(self):
        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        parser = binary_parser.EclBinaryParser(unsmry_file)
        vectors = parser.read_vectors()
        result = vectors.shape
        os.chdir(cur_dir)
        self.assertEqual(result, (1611, 5000))

    def test_get_vectors_shape(self):
        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        parser = binary_parser.EclBinaryParser(unsmry_file)
        vectors = parser.read_vectors()
        result = parser.get_vectors_shape()
        self.assertEqual(result, (1611, 5000))

    def test_get_vector_names_raw(self):
        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        parser = binary_parser.EclBinaryParser(unsmry_file)
        vectors = parser.read_vectors()
        print(vectors.columns.get_level_values(0))
        print(len(vectors.columns.get_level_values(0)))  # 5000
        print(type(vectors.columns.get_level_values(0)))
        result = set(vectors.columns.get_level_values(0))
        print(result)
        print(len(result))

    def test_get_vector_names(self):
        expected = ['COPR', 'COPT', 'CWFR', 'CWIR', 'CWPR', 'CWPT', 'FGIR', 'FGIT', 'FGLIR', 'FGOR', 'FGORH', 'FGPR',
                    'FGPT', 'FLPR', 'FLPT', 'FMCTP', 'FMWWO', 'FMWWT', 'FODEN', 'FOE', 'FOIP', 'FOPR', 'FOPRF', 'FOPRH',
                    'FOPRS', 'FOPT', 'FOPTH', 'FPR', 'FVIR', 'FVIT', 'FVPR', 'FVPT', 'FWCT', 'FWCTH', 'FWIP', 'FWIR',
                    'FWIT', 'FWPR', 'FWPT', 'GGOR', 'GGPR', 'GGPT', 'GOPR', 'GOPT', 'GVIR', 'GVIT', 'GVPR', 'GVPT',
                    'GWCT', 'GWIR', 'GWPR', 'MSUMLINS', 'RGPV', 'RHPV', 'ROE', 'ROEW', 'ROPV', 'ROSAT', 'RPR', 'RRPV',
                    'RWPV', 'TCPU', 'TIME', 'WBHP', 'WBHPH', 'WBP', 'WBP4', 'WBP9', 'WGIR', 'WGIT', 'WGLIR', 'WGOR',
                    'WGORH', 'WGPR', 'WGPRH', 'WGPTH', 'WLPR', 'WLPRH', 'WLPT', 'WLPTH', 'WMCON', 'WMCTL', 'WOPR',
                    'WOPRH', 'WOPT', 'WOPTH', 'WPI', 'WTHP', 'WTICIW1', 'WTICIW2', 'WTIRIW1', 'WTIRIW2', 'WTPCIW1',
                    'WTPCIW2', 'WTPRIW1', 'WTPRIW2', 'WWCT', 'WWCTH', 'WWIR', 'WWIRH', 'WWIT', 'WWITH', 'WWPR', 'WWPRH',
                    'WWPT', 'WWPTH', 'YEARS']

        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        parser = binary_parser.EclBinaryParser(unsmry_file)
        vectors = parser.read_vectors()
        result = sorted(set(vectors.columns.get_level_values(0)))
        # print(sorted(result))
        self.assertEqual(result, expected)

    def test_get_vector_raw(self):
        cur_dir = os.getcwd()
        volve_dir = os.path.join(os.path.dirname(os.path.dirname(binary_parser.__file__)), "volve")
        # print(volve_dir)
        unsmry_file = "VOLVE_2016.UNSMRY"
        os.chdir(volve_dir)
        parser = binary_parser.EclBinaryParser(unsmry_file)
        vectors = parser.read_vectors()
        vector_name = "FOPR"
        fopr = vectors[[vector_name]]
        fopr_us = fopr.unstack()
        fopr_us_ri = fopr_us.reset_index()
        print(fopr_us_ri[1:10])
        print(fopr_us_ri.columns)  # print df columns
        print(fopr_us_ri[0][20:30])  # select column 0, the values




