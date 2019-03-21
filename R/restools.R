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
