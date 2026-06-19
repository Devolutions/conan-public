cmake_minimum_required(VERSION 3.6)

project(cmake_wrapper)

set(CONAN_DISABLE_CHECK_COMPILER ON)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
