find_path(WinPR_INCLUDE_DIR
    NAMES winpr/winpr.h
    PATH_SUFFIXES include/winpr)

find_library(WinPR_LIBRARY
   NAMES winpr3
   PATH_SUFFIXES lib)

add_library(winpr STATIC IMPORTED)
set_property(TARGET winpr PROPERTY IMPORTED_LOCATION "${WinPR_LIBRARY}")
set_property(TARGET winpr PROPERTY INCLUDE_DIRECTORIES "${WinPR_INCLUDE_DIR}")