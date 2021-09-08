cmake_minimum_required(VERSION 3.8)

project(cmake_wrapper)

set(CONAN_DISABLE_CHECK_COMPILER ON)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
find_package(Threads REQUIRED)
list(APPEND CMAKE_REQUIRED_LIBRARIES pthread)

file(GLOB source_files CONFIGURE_DEPENDS
    "source_subfolder/sqlite3secure/src/*.h",
    "source_subfolder/sqlite3secure/src/sqlite3.def",
    "source_subfolder/sqlite3secure/src/sqlite3secure.c"
)

add_library(${PROJECT_NAME} SHARED ${source_files})
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME sqlite3secure)

add_compile_definitions("SQLITE_THREADSAFE=1")
add_compile_definitions("SQLITE_DEFAULT_PAGE_SIZE=4096")
add_compile_definitions("SQLITE_TEMP_STORE=2")
add_compile_definitions("SQLITE_DEFAULT_TEMP_CACHE_SIZE=1024")
add_compile_definitions("SQLITE_HAS_CODEC")
add_compile_definitions("SQLITE_ENABLE_COLUMN_METADATA")
add_compile_definitions("SQLITE_ENABLE_FTS4")
add_compile_definitions("SQLITE_ENABLE_FTS3_PARENTHESIS")
add_compile_definitions("SQLITE_ENABLE_RTREE")
add_compile_definitions("SQLITE_CORE")
add_compile_definitions("SQLITE_USE_URI")
add_compile_definitions("SQLITE_ALLOW_URI_AUTHORITY")
add_compile_definitions("SQLITE_SECURE_DELETE")
add_compile_definitions("SQLITE_SOUNDEX")
add_compile_definitions("CODEC_TYPE=CODEC_TYPE_AES128")