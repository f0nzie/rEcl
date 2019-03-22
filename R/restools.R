

check_python_version <- function(){
    #packageStartupMessage("Checking for the python version...")
    psys <- reticulate::import("sys")
    v <- strtoi(substr(psys$version,1,1))
    #packageStartupMessage(paste("Version",psys$version,"detected..."))
    if (v < 3){
        packageStartupMessage("Load error: pysd2r has only been tested with python3...")
        packageStartupMessage("Check to see that RETICULATE_PYTHON points to python3")
        packageStartupMessage("Use the function pysd2r::get_python_info() to check current configuration")
        stop("Exiting pysd2r.")
    }
}


check_restools_present <- function() {
    # ecl_root <- system.file(package = "rEcl")
    cur_dir <- getwd()
    python_libs_folder <- system.file("python", package = "rEcl")
    setwd(python_libs_folder)
    restools <- reticulate::import("restools")
    #return(python_libs_folder)
    setwd(cur_dir)
    restools
}


#' Connect to Python and the package restools
#'
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' }
restools_connect <- function (){
    check_python_version()
    restools <- check_restools_present()
    if(is.null(restools)){
        stop("restools error: no connection to python via rectiulate...")
    }
    structure(list(py_link=restools,
                   connected=T,
                   connect_time=Sys.time(),
                   loaded_model=F,
                   reloaded_model=F,
                   model=c()),class="pyrestools")
}


#' Call to Python class to convert Eclipse binary files
#'
#' Uses a Python package under restools to make the convertion from Eclipse
#' binary files to dataframes
#'
#' @param o object
#' @param file the name of a Eclipse binary file
#'
#' @export
#' @examples
#' \dontrun{
#' ecl_folder <- system.file("rawdata", package = "rEcl")
#' unsmry_file <- file.path(ecl_folder, "PUNQS3", "PUNQS3.UNSMRY")
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' }
EclBinaryParser <- function(o, file){
    if(o$connected == F || is.null(o))
        stop("Error, no connection made. Need to call pysd_connect() befoe read_vensim()")
    UseMethod("EclBinaryParser")
}

#' @export
EclBinaryParser.pyrestools <- function(o, file){
    tryCatch(
        {m <- o$py_link$binary_parser$EclBinaryParser(file)
        o$loaded_model <- TRUE
        o$model <- m
        o
        },
        error=function(cond) {
            packageStartupMessage("pysd2r error: cannot find file, check file path...")
            packageStartupMessage("Here's the original error message:")
            packageStartupMessage(cond)
            return(o)},
        finally={
        })
}

#' Get the dimensions of the main dataframe read from Eclipse binary file
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_dimensions(parser)
#' }
get_dimensions <- function(p) {
    p$model$get_dimens()

}

#' Get the activated cells from the reservoir model
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_actnum(parser)
#' }
get_actnum <- function(p) {
    p$model$get_actnum()

}

#' Get the seqnum sequential dates
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_seqnum_dates(parser)
#' }
get_seqnum_dates <- function(p) {
    p$model$get_seqnum_dates()

}


#' Ask if the model is of dual porosity
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' is_dual(parser)
#' }
is_dual <- function(p) {
    p$model$is_dual()

}

#' Read the vectors from the main dataframe
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' ecl_folder <- system.file("rawdata", package = "rEcl")
#' unsmry_file <- file.path(ecl_folder, "PUNQS3", "PUNQS3.UNSMRY")
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' read_vectors(parser)
#' }
read_vectors <- function(p) {
    p$model$read_vectors()
}

#' Get the shape or dimensions of the vectors dataframe
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_vectors_shape(parser)
#' }
get_vectors_shape <- function(p) {
    unl_shape <- unlist(p$model$get_vectors_shape())
    c(unl_shape[1], unl_shape[2])
}

#' Get all the names for the vectors extracted from the main dataframe
#'
#' @param p parser object
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_vectors_shape(parser)
#' }
get_vector_names <- function(p) {
    p$model$get_vector_names()
}


#' Get a column or several columns from the main dataframe
#'
#' This function has been vectorized to read multiple columns
#'
#' @param p parser object
#' @param cols character vectors with names of the columns
#' @export
#' @examples
#' \dontrun{
#' py <- restools_connect()
#' parser <- EclBinaryParser(py, unsmry_file)
#' get_vector_column(parser, "FOPR")
#' # vectorized function to get several vectors at once
#' df_vars <- get_vector_column(parser, c("YEARS", "FGOR", "FOPR", "FWCT"))
#' }
get_vector_column <- function(p, cols) {
    f <- function(x) {
        p$model$get_vector_column(x)
    }

    df <- sapply(cols, f, USE.NAMES = FALSE)
    do.call(data.frame, df)
}


# show_field_vectors <- function(p) {
#     vectors <- p$model$read_vectors()
#     # get the columns at level 0
#     vectors_columns_l0 = vectors$columns$get_level_values(0)
#     vectors_columns_l0_list = vectors_columns_l0$to_list()
#     vectors_columns_l0u <- unique(py$vectors_columns_l0_list)
#     # field vectors
#     vectors_columns_l0u[startsWith(vectors_columns_l0u, "F")]
# }