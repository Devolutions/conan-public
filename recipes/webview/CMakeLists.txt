
cmake_minimum_required(VERSION 3.2)

project(WebView C CXX)

set(CMAKE_COLOR_MAKEFILE ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake/)

find_package(PkgConfig REQUIRED)

# GTK3
pkg_check_modules(GTK3 REQUIRED gtk+-3.0)
include_directories(${GTK3_INCLUDE_DIRS})
link_directories(${GTK3_LIBRARY_DIRS})
add_definitions(${GTK3_CFLAGS_OTHER})

#libsoup
find_package(LibSoup REQUIRED)
if(LIBSOUP_FOUND)
    include_directories(${LIBSOUP_INCLUDE_DIRS})
endif()

# WebKit2
find_package(WebKit2Gtk REQUIRED)
if(WEBKIT2GTK_FOUND)
    include_directories(${WEBKIT2GTK_INCLUDE_DIRS})
    link_directories(${WEBKIT2GTK_LIBRARY_DIRS})
    add_definitions(${WEBKIT2GTK_CFLAGS_OTHER})
endif()

add_library("WebView" SHARED "src/WebView.c")

target_compile_options("WebView" PRIVATE -Wall -Werror)
target_link_libraries("WebView" ${GTK3_LIBRARIES} ${LIBSOUP_LIBRARIES} ${WEBKIT2_LIBRARIES})