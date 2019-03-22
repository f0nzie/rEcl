
<!-- README.md is generated from README.Rmd. Please edit that file -->

# rEcl

The goal of `rEcl` is to serve as a R wrapper of the class
`EclBinaryParser`, written in Python, by [Konstantin Sermyagin](). The
class converts the reservoir simulation output files generated by
Eclipse from binary to dataframes.

## Installation

For the moment, `rEcl` is only available through Github. Once is
completed it will be submitted to CRAN.

## Requirements

  - R 3.5.3
  - Rtools 3.5
  - RStudio 1.2+. *I used RStudio preview 1.2.1327 for the development
    of the package.*
  - Python Anaconda3-2018.12-Windows-x86\_64
  - Conda environment 3.6 with pandas and numpy installed. *I called
    this environment* `pyres`

## Files used for testing

For testing `rEcl` and `EclBinaryParser` I used the output binary files
from the reservoir simulation of the Volve field.

    VOLVE_2016.INIT
    VOLVE_2016.RSSPEC
    VOLVE_2016.SMSPEC
    VOLVE_2016.UNSMRY

You can find a copy of these files in this repository under
`rEcl/inst/python/volve` but the package will not install them. You will
have to copy these files manually. In the future, I plan to download the
files directly from Zenodo or Google drive, mainly, because these files
are too big for an R package.

## Functions for the class EclBinaryParser

  - `get_dimens`
  - `is_dual`
  - `get_actnum`
  - `get_seqnum_dates`
  - `read_prop_array`
  - `read_prop_time`
  - `read_vectors`

### New functions

  - `get_vectors_shape`: get the shape or dimensions of the vectors
    dataframe
  - `get_vector_names`: get the names of all the vectors
  - `get_vector_column`: get the values for a vector-column

## Examples

### SPE6

We start by reading the file `SPE6_FRAC.UNSMRY`. This file , because is
relatively small, we can include it with the package. We willread it
from the package installation folder.

``` r
library(reticulate)

reticulate::use_condaenv("pyres", required = TRUE)
reticulate::py_config()
#> python:         C:\Users\msfz751\Anaconda3\envs\pyres\python.exe
#> libpython:      C:/Users/msfz751/Anaconda3/envs/pyres/python36.dll
#> pythonhome:     C:\Users\msfz751\ANACON~1\envs\pyres
#> version:        3.6.8 |Anaconda, Inc.| (default, Feb 21 2019, 18:30:04) [MSC v.1916 64 bit (AMD64)]
#> Architecture:   64bit
#> numpy:          C:\Users\msfz751\ANACON~1\envs\pyres\lib\site-packages\numpy
#> numpy_version:  1.16.2
#> 
#> NOTE: Python version was forced by use_python function
```

``` r
library(rEcl)

ecl_folder <- system.file("rawdata", package = "rEcl")
ecl_folder
#> [1] "C:/Users/msfz751/Documents/R/win-library/3.5/rEcl/rawdata"
unsmry_file <- file.path(ecl_folder, "spe6", "SPE6_FRAC.UNSMRY")
file.exists(unsmry_file)
#> [1] TRUE
```

We connect to Python and load the class `EclBinaryParser` which resides
in the Python package called `restools`. You can take a look at
`restools` under the R installation folder in your lcoal disk.

Once we connect and load the Python package, we create an instance of
the class `EclBinaryParser` providing the parse object `py` and the full
name of the Eclipse binary file.

``` r
py <- restools_connect()
parser <- EclBinaryParser(py, unsmry_file)
```

First basic task is finding the dimensions of the reservoir model. We do
that with `get_dimensions`.

``` r
get_dimensions(parser)
#> DIMENS(ni=10, nj=1, nk=10)
```

This is a heavier operation; reading the vectors.

``` r
vectors <- read_vectors(parser)
```

Get the shape or dimensions of the vector dataframe.

``` r
get_vectors_shape(parser)
#> [1] 69 32
```

We get the names of the vectors we specified in our input file.

``` r
get_vector_names(parser)
#>  [1] "BGSAT" "BOSAT" "BPR"   "BRS"   "BWSAT" "FGOR"  "FGPR"  "FOPR" 
#>  [9] "FPR"   "TIME"  "WBHP"  "YEARS"
```

We now want a dataframe corresponding to a specific vector-column with
`get_vector_column`:

``` r
get_vector_column(parser, "FOPR")
#>           FOPR
#> 1    0.0000000
#> 2  495.8547363
#> 3  496.4673462
#> 4  497.7044983
#> 5  500.0000000
#> 6  500.0000000
#> 7  500.0000000
#> 8  500.0000000
#> 9  500.0000000
#> 10 500.0000000
#> 11 499.0129700
#> 12 495.0864258
#> 13 491.3752441
#> 14 487.6884460
#> 15 483.7983093
#> 16 479.4172058
#> 17 474.9851074
#> 18 470.4046021
#> 19 465.6196289
#> 20 460.7243347
#> 21 455.7453308
#> 22 450.6983032
#> 23 445.5942688
#> 24 440.4420471
#> 25 435.2494202
#> 26 430.0222778
#> 27 424.0520325
#> 28 416.5676270
#> 29 408.7698059
#> 30 400.7507019
#> 31 392.5427246
#> 32 384.1553650
#> 33 375.7556763
#> 34 367.2411499
#> 35 358.5085144
#> 36 349.5070496
#> 37 339.1749573
#> 38 327.4499817
#> 39 315.0457153
#> 40 301.9628906
#> 41 288.1910400
#> 42 273.9568787
#> 43 259.3403320
#> 44 243.6156769
#> 45 223.3641968
#> 46 201.8397217
#> 47 179.7216034
#> 48 157.3689117
#> 49 135.5422974
#> 50 114.8100815
#> 51  91.3848877
#> 52  66.5469284
#> 53  44.1556320
#> 54  26.0932941
#> 55  13.4400187
#> 56   5.8621721
#> 57   5.2417884
#> 58   4.5437417
#> 59   3.6096404
#> 60   2.4702997
#> 61   1.3012712
#> 62   0.4364305
#> 63   0.0000000
#> 64   0.0000000
#> 65   0.0000000
#> 66   0.0000000
#> 67   0.0000000
#> 68   0.0000000
#> 69   0.0000000
```

Finally, because the function `get_vector_column` is vectorized, we can
get a dataframe of multiple columns.

``` r
# get several vectors at once
df_vars <- get_vector_column(parser, c("FPR", "FGOR", "FOPR"))
df_vars
#>         FPR         FGOR        FOPR
#> 1  6025.137     0.000000   0.0000000
#> 2  6021.500     1.530000 495.8547363
#> 3  6010.570     1.530000 496.4673462
#> 4  5977.642     1.530000 497.7044983
#> 5  5878.311     1.530000 500.0000000
#> 6  5743.715     1.530000 500.0000000
#> 7  5609.000     1.530000 500.0000000
#> 8  5528.037     1.538324 500.0000000
#> 9  5492.169     1.562090 500.0000000
#> 10 5458.588     1.583304 500.0000000
#> 11 5426.020     1.608501 499.0129700
#> 12 5394.494     1.637577 495.0864258
#> 13 5365.298     1.668722 491.3752441
#> 14 5336.807     1.703061 487.6884460
#> 15 5307.525     1.744257 483.7983093
#> 16 5278.622     1.811011 479.4172058
#> 17 5248.898     1.894031 474.9851074
#> 18 5217.372     2.003969 470.4046021
#> 19 5185.498     2.126142 465.6196289
#> 20 5153.688     2.257681 460.7243347
#> 21 5121.876     2.397633 455.7453308
#> 22 5090.011     2.545463 450.6983032
#> 23 5058.050     2.700851 445.5942688
#> 24 5025.961     2.863592 440.4420471
#> 25 4993.717     3.033530 435.2494202
#> 26 4961.294     3.210622 430.0222778
#> 27 4927.479     3.415624 424.0520325
#> 28 4890.290     3.686419 416.5676270
#> 29 4852.142     3.985715 408.7698059
#> 30 4813.382     4.311690 400.7507019
#> 31 4773.960     4.664652 392.5427246
#> 32 4733.835     5.046370 384.1553650
#> 33 4693.025     5.447596 375.7556763
#> 34 4651.508     5.877616 367.2411499
#> 35 4609.229     6.347281 358.5085144
#> 36 4566.122     6.864860 349.5070496
#> 37 4518.661     7.555875 339.1749573
#> 38 4465.955     8.423036 327.4499817
#> 39 4411.505     9.426800 315.0457153
#> 40 4355.158    10.592511 301.9628906
#> 41 4296.767    11.953240 288.1910400
#> 42 4236.273    13.519985 273.9568787
#> 43 4173.643    15.325132 259.3403320
#> 44 4108.362    17.547583 243.6156769
#> 45 4034.673    20.967762 223.3641968
#> 46 3956.873    25.385218 201.8397217
#> 47 3875.409    31.051266 179.7216034
#> 48 3790.427    38.419727 157.3689117
#> 49 3702.283    47.972599 135.5422974
#> 50 3611.458    60.411133 114.8100815
#> 51 3515.281    81.203598  91.3848877
#> 52 3412.050   119.070526  66.5469284
#> 53 3306.926   189.455231  44.1556320
#> 54 3201.213   333.402679  26.0932941
#> 55 3096.375   662.164490  13.4400187
#> 56 2993.682  1529.078735   5.8621721
#> 57 2983.476  1709.756104   5.2417884
#> 58 2970.660  1971.567749   4.5437417
#> 59 2950.695  2479.002441   3.6096404
#> 60 2919.802  3612.904297   2.4702997
#> 61 2872.318  6819.601074   1.3012712
#> 62 2800.109 20102.908203   0.4364305
#> 63 2800.150     0.000000   0.0000000
#> 64 2800.146     0.000000   0.0000000
#> 65 2800.146     0.000000   0.0000000
#> 66 2800.146     0.000000   0.0000000
#> 67 2800.146     0.000000   0.0000000
#> 68 2800.146     0.000000   0.0000000
#> 69 2800.146     0.000000   0.0000000
```
