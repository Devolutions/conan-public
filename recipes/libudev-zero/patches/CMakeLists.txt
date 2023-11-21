cmake_minimum_required(VERSION 3.1)

set(CMAKE_C_STANDARD 99)

project(udev-zero C)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CMAKE_THREAD_PREFER_PTHREAD ON)
find_package(Threads REQUIRED)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_XOPEN_SOURCE=700")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -Wpedantic")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wmissing-prototypes -Wstrict-prototypes -Wno-unused-parameter")

add_library(udev-zero
    udev.c
    udev_list.h
    udev_list.c
    udev_device.c
    udev_monitor.c
    udev_enumerate.c)

target_link_libraries(udev-zero PRIVATE Threads::Threads)

install(TARGETS udev-zero
    DESTINATION "lib")

install(FILES "udev.h"
	DESTINATION "include"
    RENAME "libudev.h")
