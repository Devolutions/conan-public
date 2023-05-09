
cmake_minimum_required(VERSION 3.2)

project(WebView C CXX)

set(CMAKE_COLOR_MAKEFILE ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(PkgConfig REQUIRED)

# GTK3
pkg_check_modules(GTK3 REQUIRED gtk+-3.0)
include_directories(${GTK3_INCLUDE_DIRS})
link_directories(${GTK3_LIBRARY_DIRS})
add_definitions(${GTK3_CFLAGS_OTHER})

# WebKit2
pkg_check_modules(WEBKIT2 REQUIRED webkit2gtk-4.0)
include_directories(${WEBKIT2_INCLUDE_DIRS})
link_directories(${WEBKIT2_LIBRARY_DIRS})
add_definitions(${WEBKIT2_CFLAGS_OTHER})

add_library("WebView" SHARED "src/WebView.c")

target_compile_options("WebView" PRIVATE -Wall -Werror)
target_link_libraries("WebView" ${GTK3_LIBRARIES} ${WEBKIT2_LIBRARIES})