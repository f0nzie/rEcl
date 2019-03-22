# Hello, world!
#
# This is an example function named 'hello'
# which prints 'Hello, world!'.
#
# You can learn more about package authoring with RStudio at:
#
#   http://r-pkgs.had.co.nz/
#
# Some useful keyboard shortcuts for package authoring:
#
#   Install Package:           'Ctrl + Shift + B'
#   Check Package:             'Ctrl + Shift + E'
#   Test Package:              'Ctrl + Shift + T'


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


#' @export
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


#' @export
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


#' @export
get_dimensions <- function(p) {
    p$model$get_dimens()

}

#' @export
get_actnum <- function(p) {
    p$model$get_actnum()

}

#' @export
get_seqnum_dates <- function(p) {
    p$model$get_seqnum_dates()

}


#' @export
is_dual <- function(p) {
    p$model$is_dual()

}

#' @export
read_vectors <- function(p) {
    p$model$read_vectors()
}

#' @export
get_vectors_shape <- function(p) {
    unl_shape <- unlist(p$model$get_vectors_shape())
    c(unl_shape[1], unl_shape[2])
}


#' @export
get_vector_names <- function(p) {
    p$model$get_vector_names()
}


#' @export
get_vector_column <- function(p, cols) {
    f <- function(x) {
        p$model$get_vector_column(x)
    }

    df <- sapply(cols, f, USE.NAMES = FALSE)
    do.call(data.frame, df)
}


show_field_vectors <- function(p) {
    vectors <- p$model$read_vectors()
    # get the columns at level 0
    vectors_columns_l0 = vectors$columns$get_level_values(0)
    vectors_columns_l0_list = vectors_columns_l0$to_list()
    vectors_columns_l0u <- unique(py$vectors_columns_l0_list)
    # field vectors
    vectors_columns_l0u[startsWith(vectors_columns_l0u, "F")]
}