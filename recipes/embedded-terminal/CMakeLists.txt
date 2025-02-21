
cmake_minimum_required(VERSION 3.15)

project(EmbeddedTerminal C CXX)

set(CMAKE_COLOR_MAKEFILE ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(PkgConfig REQUIRED)

# GTK3
pkg_check_modules(GTK3 REQUIRED gtk+-3.0)
include_directories(${GTK3_INCLUDE_DIRS})
link_directories(${GTK3_LIBRARY_DIRS})
add_definitions(${GTK3_CFLAGS_OTHER})

# VTE
pkg_check_modules(VTE REQUIRED vte-2.91)
include_directories(${VTE_INCLUDE_DIRS})
link_directories(${VTE_LIBRARY_DIRS})
add_definitions(${VTE_CFLAGS_OTHER})

add_library("EmbeddedTerminal" SHARED "src/EmbeddedTerminal.c")

target_link_libraries("EmbeddedTerminal" ${GTK3_LIBRARIES} ${VTE_LIBRARIES})