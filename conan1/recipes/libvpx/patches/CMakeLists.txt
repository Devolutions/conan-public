
cmake_minimum_required(VERSION 3.15)

project(LIBVPX C CXX)

include(CheckIncludeFiles)
include(CMakeDependentOption)

cmake_policy(SET CMP0091 NEW)

set(CMAKE_DISABLE_IN_SOURCE_BUILD ON)

set(LIBVPX_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(LIBVPX_BIN_DIR "${CMAKE_CURRENT_BINARY_DIR}")

# detect version information

if(EXISTS "${LIBVPX_SRC_DIR}/.git")
    execute_process(
        COMMAND "git" "describe" "--match=v[0-9]*"
        WORKING_DIRECTORY "${LIBVPX_SRC_DIR}"
        OUTPUT_VARIABLE RAW_VERSION_STRING
        OUTPUT_STRIP_TRAILING_WHITESPACE)
elseif(EXISTS "${LIBVPX_SRC_DIR}/CHANGELOG")
    file(STRINGS
        "${LIBVPX_SRC_DIR}/CHANGELOG" CHANGELOG
        REGEX ".?([0-9]+)\\.([0-9]+)\\.([0-9]+)-?(.*)"
        LIMIT_COUNT 1)
    string(REGEX REPLACE "^(.*) (.*) \"(.*)\"$" "\\2" RAW_VERSION_STRING "${CHANGELOG}")
endif()

set(VERSION_REGEX "^.?([0-9]+)\\.([0-9]+)\\.([0-9]+)-?(.*)")
string(REGEX REPLACE "${VERSION_REGEX}" "\\1" VERSION_MAJOR "${RAW_VERSION_STRING}")
string(REGEX REPLACE "${VERSION_REGEX}" "\\2" VERSION_MINOR "${RAW_VERSION_STRING}")
string(REGEX REPLACE "${VERSION_REGEX}" "\\3" VERSION_PATCH "${RAW_VERSION_STRING}")
string(REGEX REPLACE "${VERSION_REGEX}" "\\4" VERSION_EXTRA "${RAW_VERSION_STRING}")
set(VERSION_STRING "v${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")

message(STATUS "libvpx version ${VERSION_STRING}")

configure_file("${LIBVPX_SRC_DIR}/vpx_version.h.in"
    "${LIBVPX_BIN_DIR}/vpx_version.h" @ONLY)

find_program(PERL_EXECUTABLE perl REQUIRED)

# semi-hardcoded configuration

if(NOT DEFINED CMAKE_POSITION_INDEPENDENT_CODE)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

if(NOT DEFINED BUILD_SHARED_LIBS)
    set(BUILD_SHARED_LIBS OFF)
endif()

option(HAVE_VPX_PORTS "Have VPX ports" ON)

option(CONFIG_DEPENDENCY_TRACKING "Dependency tracking" ON)
option(CONFIG_EXTERNAL_BUILD "External build" OFF)
option(CONFIG_INSTALL_DOCS "Install documentation" OFF)
option(CONFIG_INSTALL_BINS "Install binaries" OFF)
option(CONFIG_INSTALL_LIBS "Install libraries" ON)
option(CONFIG_INSTALL_SRCS "Install sources" OFF)
option(CONFIG_CODEC_SRCS "Codec sources" OFF)
option(INSTALL_PKG_CONFIG_FILE "Install pkg-config file" ON)

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CONFIG_DEBUG 1)
    set(CONFIG_DEBUG_LIBS 1)
endif()

option(CONFIG_GPROF "Gprof" OFF)
option(CONFIG_GCOV "Gcov" OFF)

option(CONFIG_RVCT "RVCT compiler" ON)
option(CONFIG_GCC "GCC compiler" ON)
cmake_dependent_option(CONFIG_MSVS "Visual Studio" ON "MSVC" OFF)

if(CMAKE_POSITION_INDEPENDENT_CODE)
    set(CONFIG_PIC 1)
endif()

if(CMAKE_C_BYTE_ORDER STREQUAL "BIG_ENDIAN")
    set(CONFIG_BIG_ENDIAN 1)
endif()

cmake_dependent_option(CONFIG_RUNTIME_CPU_DETECT "runtime CPU detection" ON "NOT APPLE;NOT ANDROID" OFF)

option(CONFIG_POSTPROC "post-processing" ON)
option(CONFIG_DEQUANT_TOKENS "Dequant tokens" OFF)
option(CONFIG_DC_RECON "DC recon" OFF)
option(CONFIG_SPATIAL_RESAMPLING "Spatial resampling" ON)
option(CONFIG_REALTIME_ONLY "Realtime only" OFF)
option(CONFIG_ONTHEFLY_BITPACKING "On-the-fly bit packing" OFF)
option(CONFIG_ERROR_CONCEALMENT "Error concealement" OFF)
option(CONFIG_MULTI_RES_ENCODING "Multi-resolution encoding" OFF)
option(CONFIG_TEMPORAL_DENOISING "Temporal denoising" ON)
option(CONFIG_CONSISTENT_RECODE "Consistent recode" OFF)
option(CONFIG_COEFFICIENT_RANGE_CHECKING "Coefficient range checking" OFF)
option(CONFIG_SIZE_LIMIT "Size limit" OFF)
option(CONFIG_ALWAYS_ADJUST_BPM "Always adjust BPM" OFF)
option(CONFIG_NON_GREEDY_MV "Non-greedy MV" OFF)
option(CONFIG_RATE_CTRL "Rate control" OFF)
cmake_dependent_option(CONFIG_POSTPROC_VISUALIZER "Post-processing visualizer" OFF "CONFIG_POSTPROC" OFF)

option(CONFIG_INTERNAL_STATS "Internal stats" OFF)
option(CONFIG_BITSTREAM_DEBUG "Bitstream debug" OFF)
option(CONFIG_MISMATCH_DEBUG "Mismatch debug" OFF)
option(CONFIG_FP_MB_STATS "FP MB stats" OFF)

option(CONFIG_ENCODERS "VPX encoders" ON)
option(CONFIG_DECODERS "VPX decoders" ON)

option(CONFIG_VP8 "VP8 codec" ON)
option(CONFIG_VP9 "VP9 codec" ON)

cmake_dependent_option(CONFIG_VP8_ENCODER "VP8 encoder" ON "CONFIG_VP8 AND CONFIG_ENCODERS" OFF)
cmake_dependent_option(CONFIG_VP8_DECODER "VP8 decoder" ON "CONFIG_VP8 AND CONFIG_DECODERS" OFF)

cmake_dependent_option(CONFIG_VP9_ENCODER "VP9 encoder" ON "CONFIG_VP9 AND CONFIG_DECODERS" OFF)
cmake_dependent_option(CONFIG_VP9_DECODER "VP9 decoder" ON "CONFIG_VP9 AND CONFIG_DECODERS" OFF)

cmake_dependent_option(CONFIG_VP9_HIGHBITDEPTH "VP9 high bit depth" ON "CONFIG_VP9" OFF)
cmake_dependent_option(CONFIG_VP9_POSTPROC "VP9 post-processing" ON "CONFIG_VP9;CONFIG_POSTPROC" OFF)
cmake_dependent_option(CONFIG_VP9_TEMPORAL_DENOISING "VP9 temporal denoising" OFF "CONFIG_VP9;CONFIG_TEMPORAL_DENOISING" OFF)

cmake_dependent_option(CONFIG_STATIC_MSVCRT "Static MSVC runtime" ON "MSVC" OFF)

if(CONFIG_STATIC_MSVCRT)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()

if(NOT BUILD_SHARED_LIBS)
    set(CONFIG_STATIC 1)
endif()

option(CONFIG_SMALL "Small build" OFF)

option(CONFIG_BETTER_HW_COMPATIBILITY "Better hardware compatibility" OFF)
option(CONFIG_EMULATE_HARDWARE "Emulate hardware" OFF)
option(CONFIG_EXPERIMENTAL "experimental features" OFF)

option(CONFIG_OS_SUPPORT "os support" ON)
option(CONFIG_WEBM_IO "webm I/O" ON)
option(CONFIG_LIBYUV "libyuv" ON)

# detect target processor architecture

if(DEFINED CMAKE_OSX_ARCHITECTURES AND CMAKE_OSX_ARCHITECTURES)
    list(LENGTH CMAKE_OSX_ARCHITECTURES CMAKE_OSX_ARCHITECTURES_COUNT)
    if(NOT (CMAKE_OSX_ARCHITECTURES_COUNT EQUAL 1))
        message(WARNING "CMAKE_OSX_ARCHITECTURES can only be used to specify one architecture at a time")
    endif()
    list(GET CMAKE_OSX_ARCHITECTURES 0 CMAKE_SYSTEM_PROCESSOR)
endif()

if(DEFINED CMAKE_GENERATOR_PLATFORM AND CMAKE_GENERATOR_PLATFORM)
    set(CMAKE_SYSTEM_PROCESSOR "${CMAKE_GENERATOR_PLATFORM}" CACHE STRING "" FORCE)
endif()

message(STATUS "CMAKE_SYSTEM_PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")

if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64|ARM64")
    message(STATUS "Detected ARM64 processor architecture")
    set(VPX_ARCH_ARM 1)
    set(VPX_TGT_ISA "arm64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm|^ARM")
    message(STATUS "Detected ARM processor architecture")
    set(VPX_ARCH_ARM 1)
    set(VPX_TGT_ISA "armv7")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|x64|amd64|AMD64")
    message(STATUS "Detected x86_64 processor architecture")
    set(VPX_ARCH_X86_64 1)
    set(VPX_TGT_ISA "x86_64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "x86|Win32|i386|i486|i586|i686")
    message(STATUS "Detected x86 processor architecture")
    set(VPX_ARCH_X86 1)
    set(VPX_TGT_ISA "x86")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^mips")
    message(STATUS "Detected MIPS processor architecture")
    set(VPX_ARCH_MIPS 1)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "^mips64")
        set(VPX_TGT_ISA "mips64")
    else()
        set(VPX_TGT_ISA "mips32")
    endif()
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^ppc|^powerpc")
    message(STATUS "Detected PPC processor architecture")
    set(VPX_ARCH_PPC 1)
    set(VPX_TGT_ISA "ppc64le")
else()
    message(FATAL_ERROR "Could not detect processor architecture for \"${CMAKE_SYSTEM_PROCESSOR}\"")
endif()

# detect assembler configuration

option(WITH_SIMD "SIMD optimizations" ON)

if(VPX_ARCH_X86 OR VPX_ARCH_X86_64)
    if(WIN32)
        if(VPX_ARCH_X86_64)
            set(CMAKE_ASM_NASM_OBJECT_FORMAT win64)
        else()
            set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
        endif()
    elseif(APPLE)
        if(VPX_ARCH_X86_64)
            set(CMAKE_ASM_NASM_OBJECT_FORMAT macho64)
        else()
            set(CMAKE_ASM_NASM_OBJECT_FORMAT macho)
        endif()
    else()
        if(VPX_ARCH_X86_64)
            set(CMAKE_ASM_NASM_OBJECT_FORMAT elf64)
        else()
            set(CMAKE_ASM_NASM_OBJECT_FORMAT elf)
        endif()
    endif()
    enable_language(ASM_NASM)
    set(ASM_EXT ".asm")
endif()

cmake_dependent_option(HAVE_NEON "NEON extensions" ON "VPX_ARCH_ARM;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_NEON_ASM "NEON asm extensions" OFF "VPX_ARCH_ARM;WITH_SIMD" OFF)

if(VPX_ARCH_ARM)
    if(HAVE_NEON_ASM)
        message(WARNING "NEON assembly extensions are not working yet!")
        enable_language(ASM)
    endif()
    set(ASM_EXT ".asm.S")
endif()

cmake_dependent_option(HAVE_MMX "MMX extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_SSE "SSE extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_SSE2 "SSE2 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_SSE3 "SSE3 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_SSSE3 "SSSE3 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_SSE4_1 "SSE4_1 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_AVX "AVX extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_AVX2 "AVX2 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)
cmake_dependent_option(HAVE_AVX512 "AVX512 extensions" ON "VPX_ARCH_X86 OR VPX_ARCH_X86_64;WITH_SIMD" OFF)

cmake_dependent_option(HAVE_VSX "VSX extensions" ON "VPX_ARCH_PPC;WITH_SIMD" OFF)

cmake_dependent_option(HAVE_MSA "MSA extensions" ON "VPX_ARCH_MIPS;WITH_SIMD" OFF)

if(HAVE_NEON_ASM)
    set(ADS2GAL_PL "${LIBVPX_SRC_DIR}/build/make/ads2gas.pl")
    set(ASM_HELPER "#!/bin/sh\ncat $INPUT_FILE | perl $SCRIPT_FILE -thumb -noelf > $OUTPUT_FILE\n")
    set(ASM_HELPER_SH "${LIBVPX_BIN_DIR}/asm_helper.sh")
    file(WRITE "${ASM_HELPER_SH}" "${ASM_HELPER}")
    execute_process(COMMAND "chmod" "+x" "${ASM_HELPER_SH}")
endif()

function(asm_generate)
	cmake_parse_arguments(ASM "" "INPUT;OUTPUT;SCRIPT" "" ${ARGN})
    if(NOT ASM_SCRIPT)
        set(ASM_SCRIPT "${ADS2GAL_PL}")
    endif()
    set(ASM_ARGS "-E" "env"
        "INPUT_FILE=${ASM_INPUT}"
        "SCRIPT_FILE=${ASM_SCRIPT}"
        "OUTPUT_FILE=${ASM_OUTPUT}")
    list(APPEND ASM_ARGS "${ASM_HELPER_SH}")
	add_custom_command(COMMAND ${CMAKE_COMMAND}
		ARGS ${ASM_ARGS}
		OUTPUT ${ASM_OUTPUT}
		DEPENDS ${ASM_INPUT} ${ASM_SCRIPT}
        WORKING_DIRECTORY "${LIBVPX_BIN_DIR}")
endfunction()

# compiler-specific flags

if(WIN32)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_UNICODE")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_CRT_SECURE_NO_WARNINGS")
endif()

# define "restrict" and "inline" keywords used by compiler

set(RESTRICT_KEYWORD "")

if(MSVC)
    set(INLINE_KEYWORD "__inline")
else()
    set(INLINE_KEYWORD "inline")
endif()

find_package(Threads REQUIRED)

if(CMAKE_USE_PTHREADS_INIT)
    set(HAVE_PTHREAD_H 1)
endif()

check_include_files(unistd.h HAVE_UNISTD_H)

set(RTCD_PL "${LIBVPX_SRC_DIR}/build/make/rtcd.pl")
set(RTCD_REDIRECT "open OUTPUT, '>', \$ENV{RTCD_OUTPUT} or die \"Can't create file handle: $!\"; select OUTPUT;")
set(RTCD_REDIRECT_PL "${LIBVPX_BIN_DIR}/rtcd_redirect.pl")
file(WRITE "${RTCD_REDIRECT_PL}" "${RTCD_REDIRECT}")

function(rtcd_generate)
	cmake_parse_arguments(RTCD "" "SYMBOL;CONFIG;SCRIPT;OUTPUT" "" ${ARGN})
	if(NOT RTCD_CONFIG)
        set(RTCD_CONFIG "vpx_config.mk")
	endif()
    set(RTCD_ARGS "-E" "env" "RTCD_OUTPUT=${RTCD_OUTPUT}")
    list(APPEND RTCD_ARGS "perl" "${RTCD_PL}")
    list(APPEND RTCD_ARGS
        "--arch=${VPX_TGT_ISA}"
        "--sym=${RTCD_SYMBOL}"
        "--config=${RTCD_CONFIG}"
        "${RTCD_SCRIPT}" "${RTCD_REDIRECT_PL}")
	add_custom_command(COMMAND ${CMAKE_COMMAND}
		ARGS ${RTCD_ARGS}
		OUTPUT ${RTCD_OUTPUT}
		DEPENDS ${RTCD_SCRIPT}
        WORKING_DIRECTORY "${LIBVPX_BIN_DIR}")
endfunction()

configure_file("${LIBVPX_SRC_DIR}/vpx_config.h.in"
    "${LIBVPX_BIN_DIR}/vpx_config.h" @ONLY)

file(STRINGS "${LIBVPX_BIN_DIR}/vpx_config.h" VPX_CONFIG_H
    REGEX "^#define ([0-9_A-Z]+) ([01])$")

set(VPX_CONFIG_ASM "")
foreach(VPX_DEFINE_C ${VPX_CONFIG_H})
    string(REGEX REPLACE "^#define ([0-9_A-Z]+) ([01])$"
        "\\1 equ \\2" VPX_DEFINE_ASM "${VPX_DEFINE_C}")
    set(VPX_CONFIG_ASM "${VPX_CONFIG_ASM}\n${VPX_DEFINE_ASM}")
endforeach()

file(WRITE "${LIBVPX_BIN_DIR}/vpx_config.asm" "${VPX_CONFIG_ASM}")

set(VPX_CONFIG_MK "")
set(VPX_CONFIG_MK "${VPX_CONFIG_MK}\nSRC_PATH=${LIBVPX_SRC_DIR}")
set(VPX_CONFIG_MK "${VPX_CONFIG_MK}\nSRC_PATH_BARE=${LIBVPX_SRC_DIR}")
foreach(VPX_DEFINE_C ${VPX_CONFIG_H})
    string(REGEX REPLACE "^.*([01])$" "\\1" VPX_DEFINE_VALUE "${VPX_DEFINE_C}")
    if(${VPX_DEFINE_VALUE})
        string(REGEX REPLACE "^#define ([0-9_A-Z]+) ([01])$"
            "\\1=yes" VPX_DEFINE_MK "${VPX_DEFINE_C}")
        set(VPX_CONFIG_MK "${VPX_CONFIG_MK}\n${VPX_DEFINE_MK}")
    endif()
endforeach()

file(WRITE "${LIBVPX_BIN_DIR}/vpx_config.mk" "${VPX_CONFIG_MK}")

include_directories(${LIBVPX_SRC_DIR})
include_directories(${LIBVPX_BIN_DIR})

# vpx_codec

set(LIBVPX_VPX_SRC_DIR "${LIBVPX_SRC_DIR}/vpx")

set(LIBVPX_VPX_SOURCES "")

if(CONFIG_VP8_ENCODER OR CONFIG_VP8_DECODER)
    list(APPEND LIBVPX_VPX_SOURCES
        "${LIBVPX_VPX_SRC_DIR}/vp8.h")
endif()

if(CONFIG_VP8_ENCODER)
    list(APPEND LIBVPX_VPX_SOURCES
        "${LIBVPX_VPX_SRC_DIR}/vp8cx.h")
endif()

if(CONFIG_VP8_DECODER)
    list(APPEND LIBVPX_VPX_SOURCES
        "${LIBVPX_VPX_SRC_DIR}/vp8dx.h")
endif()

list(APPEND LIBVPX_VPX_SOURCES
    "${LIBVPX_VPX_SRC_DIR}/src/vpx_decoder.c"
    "${LIBVPX_VPX_SRC_DIR}/vpx_decoder.h"
    "${LIBVPX_VPX_SRC_DIR}/src/vpx_encoder.c"
    "${LIBVPX_VPX_SRC_DIR}/vpx_encoder.h"
    "${LIBVPX_VPX_SRC_DIR}/internal/vpx_codec_internal.h"
    "${LIBVPX_VPX_SRC_DIR}/src/vpx_codec.c"
    "${LIBVPX_VPX_SRC_DIR}/src/vpx_image.c"
    "${LIBVPX_VPX_SRC_DIR}/vpx_codec.h"
    "${LIBVPX_VPX_SRC_DIR}/vpx_frame_buffer.h"
    "${LIBVPX_VPX_SRC_DIR}/vpx_image.h"
    "${LIBVPX_VPX_SRC_DIR}/vpx_integer.h"
    "${LIBVPX_VPX_SRC_DIR}/vpx_ext_ratectrl.h")

# vpx_mem

set(LIBVPX_MEM_SRC_DIR "${LIBVPX_SRC_DIR}/vpx_mem")
set(LIBVPX_MEM_SOURCES
    "${LIBVPX_MEM_SRC_DIR}/vpx_mem.c"
    "${LIBVPX_MEM_SRC_DIR}/vpx_mem.h"
    "${LIBVPX_MEM_SRC_DIR}/include/vpx_mem_intrnl.h")

# vpx_scale

set(LIBVPX_SCALE_SRC_DIR "${LIBVPX_SRC_DIR}/vpx_scale")
set(LIBVPX_SCALE_SOURCES
    "${LIBVPX_SCALE_SRC_DIR}/yv12config.h"
    "${LIBVPX_SCALE_SRC_DIR}/generic/yv12config.c"
    "${LIBVPX_SCALE_SRC_DIR}/generic/yv12extend.c"
    "${LIBVPX_SCALE_SRC_DIR}/vpx_scale_rtcd.c"
    "${LIBVPX_BIN_DIR}/vpx_scale_rtcd.h")

if(CONFIG_SPATIAL_RESAMPLING)
    list(APPEND LIBVPX_SCALE_SOURCES
        "${LIBVPX_SCALE_SRC_DIR}/vpx_scale.h"
        "${LIBVPX_SCALE_SRC_DIR}/generic/vpx_scale.c"
        "${LIBVPX_SCALE_SRC_DIR}/generic/gen_scalers.c")
endif()

if(HAVE_DSPR2)
    list(APPEND LIBVPX_SCALE_SOURCES
        "${LIBVPX_SCALE_SRC_DIR}/mips/dspr2/yv12extend_dspr2.c")
endif()

rtcd_generate(SYMBOL "vpx_scale_rtcd"
    SCRIPT "${LIBVPX_SRC_DIR}/vpx_scale/vpx_scale_rtcd.pl"
    OUTPUT "${LIBVPX_BIN_DIR}/vpx_scale_rtcd.h")

# vpx_ports

set(LIBVPX_PORTS_SRC_DIR "${LIBVPX_SRC_DIR}/vpx_ports")

set(LIBVPX_PORTS_SOURCES
    "${LIBVPX_PORTS_SRC_DIR}/bitops.h"
    "${LIBVPX_PORTS_SRC_DIR}/compiler_attributes.h"
    "${LIBVPX_PORTS_SRC_DIR}/mem.h"
    "${LIBVPX_PORTS_SRC_DIR}/msvc.h"
    "${LIBVPX_PORTS_SRC_DIR}/static_assert.h"
    "${LIBVPX_PORTS_SRC_DIR}/system_state.h"
    "${LIBVPX_PORTS_SRC_DIR}/vpx_timer.h")

if(VPX_ARCH_X86 AND HAVE_MMX)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/emms_mmx.c")
endif()

if(VPX_ARCH_X86_64 AND HAVE_MMX)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/emms_mmx.asm")
endif()

if(VPX_ARCH_X86 OR VPX_ARCH_X86_64)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/x86.h"
        "${LIBVPX_PORTS_SRC_DIR}/x86_abi_support.asm")
endif()

if(VPX_ARCH_X86_64 AND CONFIG_MSVS)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/float_control_word.asm")
endif()

if(VPX_ARCH_ARM)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/arm_cpudetect.c"
        "${LIBVPX_PORTS_SRC_DIR}/arm.h")
endif()

if(VPX_ARCH_PPC)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/ppc_cpudetect.c"
        "${LIBVPX_PORTS_SRC_DIR}/ppc.h")
endif()

if(VPX_ARCH_MIPS)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/mips_cpudetect.c"
        "${LIBVPX_PORTS_SRC_DIR}/mips.h")
endif()

if(VPX_ARCH_MIPS)
    list(APPEND LIBVPX_PORTS_SOURCES
        "${LIBVPX_PORTS_SRC_DIR}/asmdefs_mmi.h")
endif()

# vpx_dsp

set(LIBVPX_DSP_SRC_DIR "${LIBVPX_SRC_DIR}/vpx_dsp")

set(LIBVPX_DSP_SOURCES
    "${LIBVPX_DSP_SRC_DIR}/vpx_dsp_common.h"
    "${LIBVPX_DSP_SRC_DIR}/prob.h"
    "${LIBVPX_DSP_SRC_DIR}/prob.c"
    "${LIBVPX_DSP_SRC_DIR}/intrapred.c"
    "${LIBVPX_DSP_SRC_DIR}/vpx_filter.h"
    "${LIBVPX_DSP_SRC_DIR}/vpx_dsp_rtcd.c"
    "${LIBVPX_BIN_DIR}/vpx_dsp_rtcd.h")

if(HAVE_MSA)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/mips/macros_msa.h")
endif()

if(HAVE_AVX2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/bitdepth_conversion_avx2.h")
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/bitdepth_conversion_sse2.h")
endif()

if(CONFIG_ENCODERS)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/bitwriter.h"
        "${LIBVPX_DSP_SRC_DIR}/bitwriter.c"
        "${LIBVPX_DSP_SRC_DIR}/bitwriter_buffer.h"
        "${LIBVPX_DSP_SRC_DIR}/bitwriter_buffer.c"
        "${LIBVPX_DSP_SRC_DIR}/psnr.c"
        "${LIBVPX_DSP_SRC_DIR}/psnr.h")

    if(CONFIG_INTERNAL_STATS)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/ssim.c"
            "${LIBVPX_DSP_SRC_DIR}/ssim.h"
            "${LIBVPX_DSP_SRC_DIR}/psnrhvs.c"
            "${LIBVPX_DSP_SRC_DIR}/fastssim.c")
    endif()
endif()

if(CONFIG_DECODERS)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/bitreader.h"
        "${LIBVPX_DSP_SRC_DIR}/bitreader.c"
        "${LIBVPX_DSP_SRC_DIR}/bitreader_buffer.c"
        "${LIBVPX_DSP_SRC_DIR}/bitreader_buffer.h")
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/intrapred_sse2.asm")
endif()

if(HAVE_SSE3)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/intrapred_ssse3.asm")
endif()

if(HAVE_VSX)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/ppc/intrapred_vsx.c")
endif()

if(CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/highbd_intrapred_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/highbd_intrapred_intrin_sse2.c")
    endif()
    if(HAVE_SSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/highbd_intrapred_intrin_ssse3.c")
    endif()
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/highbd_intrapred_neon.c")
    endif()
endif()

if(CONFIG_POSTPROC)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/add_noise.c"
        "${LIBVPX_DSP_SRC_DIR}/deblock.c"
        "${LIBVPX_DSP_SRC_DIR}/postproc.h")
    if(HAVE_MSA)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/add_noise_msa.c"
            "${LIBVPX_DSP_SRC_DIR}/mips/deblock_msa.c")
    endif()
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/deblock_neon.c")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/add_noise_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/deblock_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/post_proc_sse2.c")
    endif()
    if(HAVE_VSX)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/ppc/deblock_vsx.c")
    endif()
endif()

if(HAVE_NEON_ASM)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/arm/intrapred_neon_asm${ASM_EXT}")
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/arm/intrapred_neon.c")
endif()

if(HAVE_MSA)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/mips/intrapred_msa.c")
endif()

if(HAVE_DSPR2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/mips/intrapred4_dspr2.c"
        "${LIBVPX_DSP_SRC_DIR}/mips/intrapred8_dspr2.c"
        "${LIBVPX_DSP_SRC_DIR}/mips/intrapred16_dspr2.c"
        "${LIBVPX_DSP_SRC_DIR}/mips/common_dspr2.h"
        "${LIBVPX_DSP_SRC_DIR}/mips/common_dspr2.c")
endif()

if(CONFIG_VP9)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/vpx_convolve.c"
        "${LIBVPX_DSP_SRC_DIR}/vpx_convolve.h")

    if(VPX_ARCH_X86 OR VPX_ARCH_X86_64)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/convolve.h")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/convolve_sse2.h")
    endif()
    if(HAVE_SSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/convolve_ssse3.h")
    endif()
    if(HAVE_AVX2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/convolve_avx2.h")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_8t_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_4t_intrin_sse2.c"
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_bilinear_sse2.asm")
    endif()
    if(HAVE_SSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_8t_ssse3.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_bilinear_ssse3.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_8t_intrin_ssse3.c")
    endif()
    if(HAVE_AVX2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/vpx_subpixel_8t_intrin_avx2.c")
    endif()
    if(CONFIG_VP9_HIGHBITDEPTH)
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/vpx_high_subpixel_8t_sse2.asm"
                "${LIBVPX_DSP_SRC_DIR}/x86/vpx_high_subpixel_bilinear_sse2.asm")
        endif()
        if(HAVE_AVX2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_convolve_avx2.c")
        endif()
        if(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/highbd_vpx_convolve_copy_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/highbd_vpx_convolve_avg_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/highbd_vpx_convolve8_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/highbd_vpx_convolve_neon.c")
        endif()
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/vpx_convolve_copy_sse2.asm")
        endif()
        if(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_scaled_convolve8_neon.c")
        endif()
        if(HAVE_NEON_ASM)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_copy_neon_asm${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_horiz_filter_type2_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_vert_filter_type2_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_horiz_filter_type1_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_vert_filter_type1_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_avg_horiz_filter_type2_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_avg_vert_filter_type2_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_avg_horiz_filter_type1_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_avg_vert_filter_type1_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_avg_neon_asm${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_neon_asm.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_neon_asm.h"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_neon.c")
        elseif(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_copy_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_avg_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve_neon.c")
        endif()
        if(HAVE_MSA)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_avg_horiz_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_avg_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_avg_vert_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_horiz_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_vert_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve_avg_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve_copy_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve_msa.h")
        endif()
        if(HAVE_MMI)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/vpx_convolve8_mmi.c")
        endif()
        if(HAVE_DSPR2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve_common_dspr2.h"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve2_avg_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve2_avg_horiz_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve2_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve2_horiz_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve2_vert_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve8_avg_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve8_avg_horiz_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve8_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve8_horiz_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/convolve8_vert_dspr2.c")
        endif()
        if(HAVE_VSX)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/ppc/vpx_convolve_vsx.c")
        endif()

        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/loopfilter.c")

        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/loopfilter_sse2.c")
        endif()
        if(HAVE_AVX2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/loopfilter_avx2.c")
        endif()
        if(HAVE_NEON_ASM)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/loopfilter_16_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/loopfilter_8_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/loopfilter_4_neon${ASM_EXT}")
        elseif(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/loopfilter_neon.c")
        endif()
        if(HAVE_MSA)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_msa.h"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_16_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_8_msa.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_4_msa.c")
        endif()
        if(HAVE_DSPR2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_filters_dspr2.h"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_filters_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_macros_dspr2.h"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_masks_dspr2.h"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_mb_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_mb_horiz_dspr2.c"
                "${LIBVPX_DSP_SRC_DIR}/mips/loopfilter_mb_vert_dspr2.c")
        endif()
        if(CONFIG_VP9_HIGHBITDEPTH)
            if(HAVE_NEON)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_loopfilter_neon.c")
            endif()
            if(HAVE_SSE2)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_loopfilter_sse2.c")
            endif()
        endif()
    endif()
endif()

list(APPEND LIBVPX_DSP_SOURCES
    "${LIBVPX_DSP_SRC_DIR}/txfm_common.h")

if(HAVE_SSE2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/txfm_common_sse2.h")
endif()
if(HAVE_MSA)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/mips/txfm_macros_msa.h")
endif()

if(CONFIG_VP9_ENCODER)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/fwd_txfm.c"
        "${LIBVPX_DSP_SRC_DIR}/fwd_txfm.h")
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_txfm_sse2.h"
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_txfm_sse2.c"
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_txfm_impl_sse2.h"
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_dct32x32_impl_sse2.h")
    endif()
    if(VPX_ARCH_X86_64 AND HAVE_SSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_txfm_ssse3_x86_64.asm")
    endif()
    if(HAVE_AVX2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_txfm_avx2.c"
            "${LIBVPX_DSP_SRC_DIR}/x86/fwd_dct32x32_impl_avx2.h")
    endif()
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/fdct_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/fdct16x16_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/fdct32x32_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/fdct_partial_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/fwd_txfm_neon.c")
    endif()
    if(HAVE_MSA)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/fwd_txfm_msa.h"
            "${LIBVPX_DSP_SRC_DIR}/mips/fwd_txfm_msa.c")
    endif()
    if(NOT CONFIG_VP9_HIGHBITDEPTH)
        if(HAVE_MSA)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/fwd_dct32x32_msa.c")
        endif()
    endif()
    if(HAVE_VSX)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/ppc/fdct32x32_vsx.c")
    endif()

    if(CONFIG_VP9)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/inv_txfm.h"
            "${LIBVPX_DSP_SRC_DIR}/inv_txfm.c")
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/inv_txfm_sse2.h"
                "${LIBVPX_DSP_SRC_DIR}/x86/inv_txfm_sse2.c"
                "${LIBVPX_DSP_SRC_DIR}/x86/inv_wht_sse2.asm")
        endif()
        if(HAVE_SSE3)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/inv_txfm_ssse3.h"
                "${LIBVPX_DSP_SRC_DIR}/x86/inv_txfm_ssse3.c")
        endif()
        if(HAVE_NEON_ASM)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/save_reg_neon${ASM_EXT}")
        endif()
        if(HAVE_VSX)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/ppc/inv_txfm_vsx.c")
        endif()

        if(CONFIG_VP9_HIGHBITDEPTH)
            if(HAVE_NEON)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct4x4_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct8x8_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct16x16_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct32x32_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct32x32_34_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct32x32_135_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct32x32_1024_add_neon.c"
                    "${LIBVPX_DSP_SRC_DIR}/arm/highbd_idct_neon.h")
            endif()
            if(HAVE_SSE2)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_inv_txfm_sse2.h"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct4x4_add_sse2.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct8x8_add_sse2.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct16x16_add_sse2.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct32x32_add_sse2.c")
            endif()
            if(HAVE_SSE4_1)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_inv_txfm_sse4.h"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct4x4_add_sse4.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct8x8_add_sse4.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct16x16_add_sse4.c"
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_idct32x32_add_sse4.c")
            endif()
        else()
            if(HAVE_MSA)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/mips/inv_txfm_msa.h"
                    "${LIBVPX_DSP_SRC_DIR}/mips/idct4x4_msa.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/idct8x8_msa.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/idct16x16_msa.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/idct32x32_msa.c")
            endif()
            if(HAVE_DSPR2)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/mips/inv_txfm_dspr2.h"
                    "${LIBVPX_DSP_SRC_DIR}/mips/itrans4_dspr2.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/itrans8_dspr2.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/itrans16_dspr2.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/itrans32_dspr2.c"
                    "${LIBVPX_DSP_SRC_DIR}/mips/itrans32_cols_dspr2.c")
            endif()
        endif()

        if(HAVE_NEON_ASM)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/idct_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct4x4_1_add_neon${ASM_EXT}"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct4x4_add_neon${ASM_EXT}")
        elseif(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/idct4x4_1_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct4x4_add_neon.c")
        endif()

        if(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/idct_neon.h"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct8x8_1_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct8x8_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct16x16_1_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct16x16_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct32x32_1_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct32x32_34_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct32x32_135_add_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/idct32x32_add_neon.c")
        endif()
    endif()

    if(CONFIG_VP9_ENCODER)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/quantize.c"
            "${LIBVPX_DSP_SRC_DIR}/quantize.h")
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/quantize_sse2.c"
                "${LIBVPX_DSP_SRC_DIR}/x86/quantize_sse2.h")
        endif()
        if(HAVE_SSSE3)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/quantize_ssse3.c"
                "${LIBVPX_DSP_SRC_DIR}/x86/quantize_ssse3.h")
        endif()
        if(HAVE_AVX)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/quantize_avx.c")
        endif()
        if(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/quantize_neon.c")
        endif()
        if(HAVE_VSX)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/ppc/quantize_vsx.c")
        endif()
        if(CONFIG_VP9_HIGHBITDEPTH)
            if(HAVE_SSE2)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/x86/highbd_quantize_intrin_sse2.c")
            endif()
        endif()

        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/avg.c")
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/avg_intrin_sse2.c")
        endif()
        if(HAVE_AVX2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/avg_intrin_avx2.c")
        endif()
        if(HAVE_NEON)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/arm/avg_neon.c"
                "${LIBVPX_DSP_SRC_DIR}/arm/hadamard_neon.c")
        endif()
        if(HAVE_MSA)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/mips/avg_msa.c")
        endif()
        if(VPX_ARCH_X86_64)
            if(HAVE_SSSE3)
                list(APPEND LIBVPX_DSP_SOURCES
                    "${LIBVPX_DSP_SRC_DIR}/x86/avg_ssse3_x86_64.asm")
            endif()
        endif()
        if(HAVE_VSX)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/ppc/hadamard_vsx.c")
        endif()
    endif()
endif()

list(APPEND LIBVPX_DSP_SOURCES
    "${LIBVPX_DSP_SRC_DIR}/skin_detection.h"
    "${LIBVPX_DSP_SRC_DIR}/skin_detection.c")

if(CONFIG_ENCODERS)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/sad.c"
        "${LIBVPX_DSP_SRC_DIR}/subtract.c"
        "${LIBVPX_DSP_SRC_DIR}/sum_squares.c")
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/sum_squares_neon.c")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sum_squares_sse2.c")
    endif()
    if(HAVE_MSA)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/sum_squares_msa.c")
    endif()
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/sad4d_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/sad_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/subtract_neon.c")
    endif()
    if(HAVE_MSA)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/sad_msa.c"
            "${LIBVPX_DSP_SRC_DIR}/mips/subtract_msa.c")
    endif()
    if(HAVE_MMI)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/sad_mmi.c"
            "${LIBVPX_DSP_SRC_DIR}/mips/subtract_mmi.c")
    endif()
    if(HAVE_SSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad_sse3.asm")
    endif()
    if(HAVE_SSSE3)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad_ssse3.asm")
    endif()
    if(HAVE_SSE4_1)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad_sse4.asm")
    endif()
    if(HAVE_AVX2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad4d_avx2.c"
            "${LIBVPX_DSP_SRC_DIR}/x86/sad_avx2.c")
    endif()
    if(HAVE_AVX512)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad4d_avx512.c")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/sad4d_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/sad_sse2.asm"
            "${LIBVPX_DSP_SRC_DIR}/x86/subtract_sse2.asm")
    endif()
    if(HAVE_VSX)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/ppc/sad_vsx.c"
            "${LIBVPX_DSP_SRC_DIR}/ppc/subtract_vsx.c")
    endif()
    if(CONFIG_VP9_HIGHBITDEPTH)
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_sad4d_sse2.asm"
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_sad_sse2.asm")
        endif()
    endif()
endif()

if(CONFIG_ENCODERS OR CONFIG_POSTPROC OR CONFIG_VP9_POSTPROC)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/variance.c"
        "${LIBVPX_DSP_SRC_DIR}/variance.h")
    if(HAVE_NEON)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/arm/avg_pred_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/subpel_variance_neon.c"
            "${LIBVPX_DSP_SRC_DIR}/arm/variance_neon.c")
    endif()
    if(HAVE_MSA)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/variance_msa.c"
            "${LIBVPX_DSP_SRC_DIR}/mips/sub_pixel_variance_msa.c")
    endif()
    if(HAVE_MMI)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/mips/variance_mmi.c")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/avg_pred_sse2.c"
            "${LIBVPX_DSP_SRC_DIR}/x86/variance_sse2.c")
    endif()
    if(HAVE_AVX2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/variance_avx2.c")
    endif()
    if(HAVE_VSX)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/ppc/variance_vsx.c")
    endif()
    if(VPX_ARCH_X86_64)
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/ssim_opt_x86_64.asm")
        endif()
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_DSP_SOURCES
            "${LIBVPX_DSP_SRC_DIR}/x86/subpel_variance_sse2.asm")
    endif()
    if(CONFIG_VP9_HIGHBITDEPTH)
        if(HAVE_SSE2)
            list(APPEND LIBVPX_DSP_SOURCES
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_variance_sse2.c"
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_variance_impl_sse2.asm"
                "${LIBVPX_DSP_SRC_DIR}/x86/highbd_subpel_variance_impl_sse2.asm")
        endif()
    endif()
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/arm/mem_neon.h"
        "${LIBVPX_DSP_SRC_DIR}/arm/sum_neon.h"
        "${LIBVPX_DSP_SRC_DIR}/arm/transpose_neon.h"
        "${LIBVPX_DSP_SRC_DIR}/arm/vpx_convolve8_neon.h")
endif()

if(HAVE_VSX)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/ppc/types_vsx.h"
        "${LIBVPX_DSP_SRC_DIR}/ppc/txfm_common_vsx.h"
        "${LIBVPX_DSP_SRC_DIR}/ppc/transpose_vsx.h"
        "${LIBVPX_DSP_SRC_DIR}/ppc/bitdepth_conversion_vsx.h")
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_DSP_SOURCES
        "${LIBVPX_DSP_SRC_DIR}/x86/mem_sse2.h"
        "${LIBVPX_DSP_SRC_DIR}/x86/transpose_sse2.h")
endif()

rtcd_generate(SYMBOL "vpx_dsp_rtcd"
    SCRIPT "${LIBVPX_SRC_DIR}/vpx_dsp/vpx_dsp_rtcd_defs.pl"
    OUTPUT "${LIBVPX_BIN_DIR}/vpx_dsp_rtcd.h")

# vpx_util

set(LIBVPX_UTIL_SRC_DIR "${LIBVPX_SRC_DIR}/vpx_util")

set(LIBVPX_UTIL_SOURCES
    "${LIBVPX_UTIL_SRC_DIR}/vpx_atomics.h"
    "${LIBVPX_UTIL_SRC_DIR}/vpx_thread.c"
    "${LIBVPX_UTIL_SRC_DIR}/vpx_thread.h"
    "${LIBVPX_UTIL_SRC_DIR}/endian_inl.h"
    "${LIBVPX_UTIL_SRC_DIR}/vpx_write_yuv_frame.h"
    "${LIBVPX_UTIL_SRC_DIR}/vpx_write_yuv_frame.c"
    "${LIBVPX_UTIL_SRC_DIR}/vpx_timestamp.h")

if(CONFIG_BITSTREAM_DEBUG OR CONFIG_MISMATCH_DEBUG)
    list(APPEND LIBVPX_UTIL_SOURCES
        "${LIBVPX_UTIL_SRC_DIR}/vpx_debug_util.h"
        "${LIBVPX_UTIL_SRC_DIR}/vpx_debug_util.c")
endif()

# vp8

set(LIBVPX_VP8_SRC_DIR "${LIBVPX_SRC_DIR}/vp8")

# vp8_common

set(LIBVPX_VP8_COMMON_SOURCES
    "${LIBVPX_VP8_SRC_DIR}/common/ppflags.h"
    "${LIBVPX_VP8_SRC_DIR}/common/onyx.h"
    "${LIBVPX_VP8_SRC_DIR}/common/onyxd.h"
    "${LIBVPX_VP8_SRC_DIR}/common/alloccommon.c"
    "${LIBVPX_VP8_SRC_DIR}/common/blockd.c"
    "${LIBVPX_VP8_SRC_DIR}/common/coefupdateprobs.h"
    "${LIBVPX_VP8_SRC_DIR}/common/default_coef_probs.h"
    "${LIBVPX_VP8_SRC_DIR}/common/dequantize.c"
    "${LIBVPX_VP8_SRC_DIR}/common/entropy.c"
    "${LIBVPX_VP8_SRC_DIR}/common/entropymode.c"
    "${LIBVPX_VP8_SRC_DIR}/common/entropymv.c"
    "${LIBVPX_VP8_SRC_DIR}/common/extend.c"
    "${LIBVPX_VP8_SRC_DIR}/common/filter.c"
    "${LIBVPX_VP8_SRC_DIR}/common/filter.h"
    "${LIBVPX_VP8_SRC_DIR}/common/findnearmv.c"
    "${LIBVPX_VP8_SRC_DIR}/common/generic/systemdependent.c"
    "${LIBVPX_VP8_SRC_DIR}/common/idct_blk.c"
    "${LIBVPX_VP8_SRC_DIR}/common/idctllm.c"
    "${LIBVPX_VP8_SRC_DIR}/common/alloccommon.h"
    "${LIBVPX_VP8_SRC_DIR}/common/blockd.h"
    "${LIBVPX_VP8_SRC_DIR}/common/common.h"
    "${LIBVPX_VP8_SRC_DIR}/common/entropy.h"
    "${LIBVPX_VP8_SRC_DIR}/common/entropymode.h"
    "${LIBVPX_VP8_SRC_DIR}/common/entropymv.h"
    "${LIBVPX_VP8_SRC_DIR}/common/extend.h"
    "${LIBVPX_VP8_SRC_DIR}/common/findnearmv.h"
    "${LIBVPX_VP8_SRC_DIR}/common/header.h"
    "${LIBVPX_VP8_SRC_DIR}/common/invtrans.h"
    "${LIBVPX_VP8_SRC_DIR}/common/loopfilter.h"
    "${LIBVPX_VP8_SRC_DIR}/common/modecont.h"
    "${LIBVPX_VP8_SRC_DIR}/common/mv.h"
    "${LIBVPX_VP8_SRC_DIR}/common/onyxc_int.h"
    "${LIBVPX_VP8_SRC_DIR}/common/quant_common.h"
    "${LIBVPX_VP8_SRC_DIR}/common/reconinter.h"
    "${LIBVPX_VP8_SRC_DIR}/common/reconintra.h"
    "${LIBVPX_VP8_SRC_DIR}/common/reconintra4x4.h"
    "${LIBVPX_VP8_SRC_DIR}/common/rtcd.c"
    "${LIBVPX_VP8_SRC_DIR}/common/setupintrarecon.h"
    "${LIBVPX_VP8_SRC_DIR}/common/swapyv12buffer.h"
    "${LIBVPX_VP8_SRC_DIR}/common/systemdependent.h"
    "${LIBVPX_VP8_SRC_DIR}/common/threading.h"
    "${LIBVPX_VP8_SRC_DIR}/common/treecoder.h"
    "${LIBVPX_VP8_SRC_DIR}/common/vp8_loopfilter.c"
    "${LIBVPX_VP8_SRC_DIR}/common/loopfilter_filters.c"
    "${LIBVPX_VP8_SRC_DIR}/common/mbpitch.c"
    "${LIBVPX_VP8_SRC_DIR}/common/modecont.c"
    "${LIBVPX_VP8_SRC_DIR}/common/quant_common.c"
    "${LIBVPX_VP8_SRC_DIR}/common/reconinter.c"
    "${LIBVPX_VP8_SRC_DIR}/common/reconintra.c"
    "${LIBVPX_VP8_SRC_DIR}/common/reconintra4x4.c"
    "${LIBVPX_VP8_SRC_DIR}/common/setupintrarecon.c"
    "${LIBVPX_VP8_SRC_DIR}/common/swapyv12buffer.c"
    "${LIBVPX_VP8_SRC_DIR}/common/vp8_entropymodedata.h"
    "${LIBVPX_BIN_DIR}/vp8_rtcd.h")

list(APPEND LIBVPX_VP8_COMMON_SOURCES
    "${LIBVPX_VP8_SRC_DIR}/common/treecoder.c")

if(VPX_ARCH_X86 OR VPX_ARCH_X86_64)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/x86/vp8_asm_stubs.c"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/loopfilter_x86.c")
endif()

if(CONFIG_POSTPROC)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/mfqe.c"
        "${LIBVPX_VP8_SRC_DIR}/common/postproc.h"
        "${LIBVPX_VP8_SRC_DIR}/common/postproc.c")
endif()

if(HAVE_MMX)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/x86/dequantize_mmx.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/idct_blk_mmx.c"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/idctllm_mmx.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/recon_mmx.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/subpixel_mmx.asm")
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/x86/idct_blk_sse2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/idctllm_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/recon_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/bilinear_filter_sse2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/subpixel_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/loopfilter_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/common/x86/iwalsh_sse2.asm")
endif()

if(HAVE_SSE3)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/x86/subpixel_ssse3.asm")
endif()

if(CONFIG_POSTPROC)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP8_COMMON_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/common/x86/mfqe_sse2.asm")
    endif()
endif()

if(VPX_ARCH_X86_64)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP8_COMMON_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/common/x86/loopfilter_block_sse2_x86_64.asm")
    endif()
endif()

if(HAVE_DSPR2)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/idctllm_dspr2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/filter_dspr2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/vp8_loopfilter_filters_dspr2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/reconinter_dspr2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/idct_blk_dspr2.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/dspr2/dequantize_dspr2.c")
endif()

if(HAVE_MSA)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/bilinear_filter_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/copymem_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/idct_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/loopfilter_filters_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/sixtap_filter_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/vp8_macros_msa.h")
endif()

if(HAVE_MMI)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/sixtap_filter_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/loopfilter_filters_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/idctllm_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/dequantize_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/copymem_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/common/mips/mmi/idct_blk_mmi.c")
endif()

if(CONFIG_POSTPROC)
    if(HAVE_MSA)
        list(APPEND LIBVPX_VP8_COMMON_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/common/mips/msa/mfqe_msa.c")
    endif()
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_VP8_COMMON_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/arm/loopfilter_arm.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/loopfilter_arm.h"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/bilinearpredict_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/copymem_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/dc_only_idct_add_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/dequant_idct_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/dequantizeb_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/idct_blk_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/iwalsh_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/vp8_loopfilter_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/loopfiltersimplehorizontaledge_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/loopfiltersimpleverticaledge_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/mbloopfilter_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/shortidct4x4llm_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/common/arm/neon/sixtappredict_neon.c")
endif()

rtcd_generate(SYMBOL "vp8_rtcd"
    SCRIPT "${LIBVPX_SRC_DIR}/vp8/common/rtcd_defs.pl"
    OUTPUT "${LIBVPX_BIN_DIR}/vp8_rtcd.h")

# vp8_encoder

set(LIBVPX_VP8_ENCODER_SOURCES
    "${LIBVPX_VP8_SRC_DIR}/vp8_cx_iface.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/defaultcoefcounts.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/bitstream.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/boolhuff.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/copy_c.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/dct.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodeframe.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodeframe.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodeintra.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodemb.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodemv.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/block.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/boolhuff.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/bitstream.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodeintra.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodemb.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/encodemv.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/firstpass.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/lookahead.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/lookahead.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/mcomp.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/modecosts.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/onyx_int.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/pickinter.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/quantize.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/ratectrl.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/rdopt.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/tokenize.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/treewriter.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/mcomp.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/modecosts.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/onyx_if.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/pickinter.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/picklpf.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/picklpf.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/vp8_quantize.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/ratectrl.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/rdopt.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/segmentation.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/segmentation.h"
    "${LIBVPX_VP8_SRC_DIR}/common/vp8_skin_detection.c"
    "${LIBVPX_VP8_SRC_DIR}/common/vp8_skin_detection.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/tokenize.c"
    "${LIBVPX_VP8_SRC_DIR}/encoder/dct_value_cost.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/dct_value_tokens.h"
    "${LIBVPX_VP8_SRC_DIR}/encoder/treewriter.c")

if(CONFIG_MULTITHREAD)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/ethreading.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/ethreading.h")
endif()

if(CONFIG_TEMPORAL_DENOISING)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/denoising.h"
        "${LIBVPX_VP8_SRC_DIR}/encoder/denoising.c")
endif()

if(CONFIG_INTERNAL_STATS)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/common/postproc.h"
        "${LIBVPX_VP8_SRC_DIR}/common/postproc.c")
endif()

if(CONFIG_MULTI_RES_ENCODING)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/mr_dissim.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/mr_dissim.h")
endif()

if(NOT CONFIG_REALTIME_ONLY)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/firstpass.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/temporal_filter.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/temporal_filter.h")
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/copy_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/copy_sse3.asm"
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/dct_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/fwalsh_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/vp8_quantize_sse2.c")
endif()

if(HAVE_SSSE3)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/vp8_quantize_ssse3.c")
endif()

if(HAVE_SSE4_1)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/quantize_sse4.c")
endif()

if(CONFIG_TEMPORAL_DENOISING)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP8_ENCODER_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/encoder/x86/denoising_sse2.c")
    endif()
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/block_error_sse2.asm"
        "${LIBVPX_VP8_SRC_DIR}/encoder/x86/vp8_enc_stubs_sse2.c")

    if(NOT CONFIG_REALTIME_ONLY)
        list(APPEND LIBVPX_VP8_ENCODER_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/encoder/x86/temporal_filter_apply_sse2.asm")
    endif()
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/arm/neon/denoising_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/arm/neon/fastquantizeb_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/arm/neon/shortfdct_neon.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/arm/neon/vp8_shortwalsh4x4_neon.c")
endif()

if(HAVE_MSA)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/mips/msa/dct_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/mips/msa/encodeopt_msa.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/mips/msa/quantize_msa.c")

    if(NOT CONFIG_REALTIME_ONLY)
        list(APPEND LIBVPX_VP8_ENCODER_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/encoder/mips/msa/temporal_filter_msa.c")
    endif()
endif()

if(HAVE_MMI)
    list(APPEND LIBVPX_VP8_ENCODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/encoder/mips/mmi/vp8_quantize_mmi.c"
        "${LIBVPX_VP8_SRC_DIR}/encoder/mips/mmi/dct_mmi.c")
endif()

if(CONFIG_TEMPORAL_DENOISING)
    if(HAVE_MSA)
        list(APPEND LIBVPX_VP8_ENCODER_SOURCES
            "${LIBVPX_VP8_SRC_DIR}/encoder/mips/msa/denoising_msa.c")
    endif()
endif()

# vp8_decoder

set(LIBVPX_VP8_DECODER_SOURCES
    "${LIBVPX_VP8_SRC_DIR}/vp8_dx_iface.c"
    "${LIBVPX_VP8_SRC_DIR}/decoder/dboolhuff.c"
    "${LIBVPX_VP8_SRC_DIR}/decoder/decodemv.c"
    "${LIBVPX_VP8_SRC_DIR}/decoder/decodeframe.c"
    "${LIBVPX_VP8_SRC_DIR}/decoder/detokenize.c"
    "${LIBVPX_VP8_SRC_DIR}/decoder/dboolhuff.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/decodemv.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/decoderthreading.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/detokenize.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/onyxd_int.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/treereader.h"
    "${LIBVPX_VP8_SRC_DIR}/decoder/onyxd_if.c")

if(CONFIG_ERROR_CONCEALMENT)
    list(APPEND LIBVPX_VP8_DECODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/decoder/ec_types.h"
        "${LIBVPX_VP8_SRC_DIR}/decoder/error_concealment.h"
        "${LIBVPX_VP8_SRC_DIR}/decoder/error_concealment.c")
endif()

if(CONFIG_MULTITHREAD)
    list(APPEND LIBVPX_VP8_DECODER_SOURCES
        "${LIBVPX_VP8_SRC_DIR}/decoder/threading.c")
endif()

# vp8

if(CONFIG_VP8)
    list(APPEND LIBVPX_VP8_SOURCES ${LIBVPX_VP8_COMMON_SOURCES})

    if(CONFIG_VP8_ENCODER)
        list(APPEND LIBVPX_VP8_SOURCES ${LIBVPX_VP8_ENCODER_SOURCES})
    endif()

    if(CONFIG_VP8_DECODER)
        list(APPEND LIBVPX_VP8_SOURCES ${LIBVPX_VP8_DECODER_SOURCES})
    endif()
endif()

# vp9

set(LIBVPX_VP9_SRC_DIR "${LIBVPX_SRC_DIR}/vp9")

# vp9_common

set(LIBVPX_VP9_COMMON_SOURCES
    "${LIBVPX_VP9_SRC_DIR}/vp9_iface_common.h"
    "${LIBVPX_VP9_SRC_DIR}/vp9_iface_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_ppflags.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_alloccommon.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_blockd.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropy.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropymode.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropymv.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_frame_buffers.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_frame_buffers.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_idct.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_alloccommon.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_blockd.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropy.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropymode.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_entropymv.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_enums.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_filter.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_filter.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_idct.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_loopfilter.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_thread_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_mv.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_onyxc_int.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_pred_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_pred_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_quant_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_reconinter.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_reconintra.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_rtcd.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_scale.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_scale.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_seg_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_seg_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_tile_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_tile_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_loopfilter.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_thread_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_mvref_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_mvref_common.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_quant_common.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_reconinter.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_reconintra.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_common_data.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_common_data.h"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_scan.c"
    "${LIBVPX_VP9_SRC_DIR}/common/vp9_scan.h"
    "${LIBVPX_BIN_DIR}/vp9_rtcd.h")

if(CONFIG_VP9_POSTPROC)
    list(APPEND LIBVPX_VP9_COMMON_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/common/vp9_postproc.h"
        "${LIBVPX_VP9_SRC_DIR}/common/vp9_postproc.c"
        "${LIBVPX_VP9_SRC_DIR}/common/vp9_mfqe.h"
        "${LIBVPX_VP9_SRC_DIR}/common/vp9_mfqe.c")
endif()

if(NOT CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_MSA)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/mips/msa/vp9_idct4x4_msa.c"
            "${LIBVPX_VP9_SRC_DIR}/common/mips/msa/vp9_idct8x8_msa.c"
            "${LIBVPX_VP9_SRC_DIR}/common/mips/msa/vp9_idct16x16_msa.c")
    endif()
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP9_COMMON_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/common/x86/vp9_idct_intrin_sse2.c")
endif()

if(HAVE_VSX)
    list(APPEND LIBVPX_VP9_COMMON_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/common/ppc/vp9_idct_vsx.c")
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_VP9_COMMON_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_iht4x4_add_neon.c"
        "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_iht8x8_add_neon.c"
        "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_iht16x16_add_neon.c"
        "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_iht_neon.h")
endif()

if(CONFIG_VP9_POSTPROC)
    if(HAVE_MSA)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/mips/msa/vp9_mfqe_msa.c")
    endif()
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/x86/vp9_mfqe_sse2.asm")
    endif()
endif()

if(NOT CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_DSPR2)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/mips/dspr2/vp9_itrans4_dspr2.c"
            "${LIBVPX_VP9_SRC_DIR}/common/mips/dspr2/vp9_itrans8_dspr2.c"
            "${LIBVPX_VP9_SRC_DIR}/common/mips/dspr2/vp9_itrans16_dspr2.c")
    endif()
else()
    if(HAVE_NEON)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_highbd_iht4x4_add_neon.c"
            "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_highbd_iht8x8_add_neon.c"
            "${LIBVPX_VP9_SRC_DIR}/common/arm/neon/vp9_highbd_iht16x16_add_neon.c")
    endif()
    if(HAVE_SSE4_1)
        list(APPEND LIBVPX_VP9_COMMON_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/x86/vp9_highbd_iht4x4_add_sse4.c"
            "${LIBVPX_VP9_SRC_DIR}/common/x86/vp9_highbd_iht8x8_add_sse4.c"
            "${LIBVPX_VP9_SRC_DIR}/common/x86/vp9_highbd_iht16x16_add_sse4.c")
    endif()
endif()

rtcd_generate(SYMBOL "vp9_rtcd"
    SCRIPT "${LIBVPX_SRC_DIR}/vp9/common/vp9_rtcd_defs.pl"
    OUTPUT "${LIBVPX_BIN_DIR}/vp9_rtcd.h")

# vp9_encoder

set(LIBVPX_VP9_ENCODER_SOURCES
    "${LIBVPX_VP9_SRC_DIR}/vp9_cx_iface.c"
    "${LIBVPX_VP9_SRC_DIR}/vp9_cx_iface.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_bitstream.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_context_tree.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_context_tree.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_cost.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_cost.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_dct.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodeframe.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodeframe.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodemb.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodemv.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ethread.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ethread.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_extend.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_block.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_bitstream.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodemb.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encodemv.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_extend.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_firstpass.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_frame_scale.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_job_queue.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_lookahead.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_lookahead.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_mcomp.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_multi_thread.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_multi_thread.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encoder.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_quantize.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ratectrl.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_rd.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_rdopt.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_pickmode.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_svc_layercontext.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_tokenize.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_treewriter.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_mcomp.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_encoder.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_picklpf.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_picklpf.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_quantize.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ratectrl.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_rd.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_rdopt.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_pickmode.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_partition_models.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_segmentation.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_segmentation.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_speed_features.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_speed_features.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_subexp.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_subexp.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_svc_layercontext.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_resize.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_resize.h")

if(CONFIG_VP9_TEMPORAL_DENOISING)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_denoiser.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_denoiser.h")
endif()

if(CONFIG_INTERNAL_STATS)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_blockiness.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_blockiness.h")
endif()

if(CONFIG_NON_GREEDY_MV)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_non_greedy_mv.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_non_greedy_mv.h")
endif()

list(APPEND LIBVPX_VP9_ENCODER_SOURCES
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_tokenize.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_treewriter.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_cyclicrefresh.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_cyclicrefresh.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_skin_detection.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_skin_detection.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_noise_estimate.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_noise_estimate.h"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ext_ratectrl.c"
    "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_ext_ratectrl.h")

if(CONFIG_VP9_POSTPROC)
    if(CONFIG_INTERNAL_STATS)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/common/vp9_postproc.h"
            "${LIBVPX_VP9_SRC_DIR}/common/vp9_postproc.c")
    endif()
endif()

if(NOT CONFIG_REALTIME_ONLY)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_firstpass.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_temporal_filter.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_temporal_filter.h"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_mbgraph.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_mbgraph.h"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_alt_ref_aq.h"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_alt_ref_aq.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_variance.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_variance.h"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_360.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_360.h"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_complexity.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/vp9_aq_complexity.h")

    if(HAVE_SSE4_1)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/x86/temporal_filter_sse4.c"
            "${LIBVPX_VP9_SRC_DIR}/encoder/x86/temporal_filter_constants.h")
    endif()
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_quantize_sse2.c")
endif()

if(HAVE_AVX2)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_quantize_avx2.c")
endif()

if(HAVE_AVX)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_diamond_search_sad_avx.c")
endif()

if(CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_highbd_block_error_intrin_sse2.c")
    endif()
    if(NOT CONFIG_REALTIME_ONLY)
        if(HAVE_SSE4_1)
            list(APPEND LIBVPX_VP9_ENCODER_SOURCES
                "${LIBVPX_VP9_SRC_DIR}/encoder/x86/highbd_temporal_filter_sse4.c")
        endif()
    endif()
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_dct_sse2.asm"
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_error_sse2.asm")
endif()

if(VPX_ARCH_X86_64)
    if(HAVE_SSSE3)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_quantize_ssse3_x86_64.asm")
    endif()
endif()

if(HAVE_SSE2)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_dct_intrin_sse2.c")
endif()

if(HAVE_SSSE3)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_frame_scale_ssse3.c")
endif()

if(CONFIG_VP9_TEMPORAL_DENOISING)
    if(HAVE_SSE2)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_denoiser_sse2.c")
    endif()
    if(HAVE_NEON)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/arm/neon/vp9_denoiser_neon.c")
    endif()
endif()

if(HAVE_AVX2)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/x86/vp9_error_avx2.c")
endif()

if(NOT CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_NEON)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/arm/neon/vp9_error_neon.c")
    endif()
endif()

if(HAVE_NEON)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/arm/neon/vp9_frame_scale_neon.c"
        "${LIBVPX_VP9_SRC_DIR}/encoder/arm/neon/vp9_quantize_neon.c")
endif()

if(HAVE_MSA)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/mips/msa/vp9_error_msa.c")
endif()

if(NOT CONFIG_VP9_HIGHBITDEPTH)
    if(HAVE_MSA)
        list(APPEND LIBVPX_VP9_ENCODER_SOURCES
            "${LIBVPX_VP9_SRC_DIR}/encoder/mips/msa/vp9_fdct4x4_msa.c"
            "${LIBVPX_VP9_SRC_DIR}/encoder/mips/msa/vp9_fdct8x8_msa.c"
            "${LIBVPX_VP9_SRC_DIR}/encoder/mips/msa/vp9_fdct16x16_msa.c"
            "${LIBVPX_VP9_SRC_DIR}/encoder/mips/msa/vp9_fdct_msa.h")
    endif()
endif()

if(HAVE_VSX)
    list(APPEND LIBVPX_VP9_ENCODER_SOURCES
        "${LIBVPX_VP9_SRC_DIR}/encoder/ppc/vp9_quantize_vsx.c")
endif()

# v9_decoder

set(LIBVPX_VP9_DECODER_SOURCES
    "${LIBVPX_VP9_SRC_DIR}/vp9_dx_iface.c"
    "${LIBVPX_VP9_SRC_DIR}/vp9_dx_iface.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decodemv.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decodeframe.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decodeframe.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_detokenize.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decodemv.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_detokenize.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decoder.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_decoder.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_dsubexp.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_dsubexp.h"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_job_queue.c"
    "${LIBVPX_VP9_SRC_DIR}/decoder/vp9_job_queue.h")

# vp9

if(CONFIG_VP9)
    list(APPEND LIBVPX_VP9_SOURCES ${LIBVPX_VP9_COMMON_SOURCES})

    if(CONFIG_VP9_ENCODER)
        list(APPEND LIBVPX_VP9_SOURCES ${LIBVPX_VP9_ENCODER_SOURCES})
    endif()

    if(CONFIG_VP9_DECODER)
        list(APPEND LIBVPX_VP9_SOURCES ${LIBVPX_VP9_DECODER_SOURCES})
    endif()
endif()

# libvpx

set(LIBVPX_HEADERS
    "${LIBVPX_SRC_DIR}/vpx/vpx_codec.h"
    "${LIBVPX_SRC_DIR}/vpx/vpx_frame_buffer.h"
    "${LIBVPX_SRC_DIR}/vpx/vpx_image.h"
    "${LIBVPX_SRC_DIR}/vpx/vpx_integer.h")

if(CONFIG_ENCODERS OR CONFIG_DECODERS)
    list(APPEND LIBVPX_HEADERS
        "${LIBVPX_SRC_DIR}/vpx/vp8.h")
endif()

if(CONFIG_ENCODERS)
    list(APPEND LIBVPX_HEADERS
        "${LIBVPX_SRC_DIR}/vpx/vp8cx.h"
        "${LIBVPX_SRC_DIR}/vpx/vpx_encoder.h"
        "${LIBVPX_SRC_DIR}/vpx/vpx_ext_ratectrl.h")
endif()

if(CONFIG_DECODERS)
    list(APPEND LIBVPX_HEADERS
        "${LIBVPX_SRC_DIR}/vpx/vp8dx.h"
        "${LIBVPX_SRC_DIR}/vpx/vpx_decoder.h")
endif()

set(LIBVPX_SOURCES
    ${LIBVPX_VPX_SOURCES}
    ${LIBVPX_MEM_SOURCES}
    ${LIBVPX_SCALE_SOURCES}
    ${LIBVPX_PORTS_SOURCES}
    ${LIBVPX_DSP_SOURCES}
    ${LIBVPX_UTIL_SOURCES}
    ${LIBVPX_VP8_SOURCES}
    ${LIBVPX_VP9_SOURCES})

set(MMX_SRC_FLAGS "-mmmx")
set(SSE2_SRC_FLAGS "-msse2")
set(SSE3_SRC_FLAGS "-msse3")
set(SSSE3_SRC_FLAGS "-mssse3")
set(SSE4_SRC_FLAGS "-msse4.1")
set(AVX_SRC_FLAGS "-mavx")
set(AVX2_SRC_FLAGS "-mavx2")
set(AVX512_SRC_FLAGS "-mavx512f -mavx512cd -mavx512bw -mavx512dq -mavx512vl")
set(VSX_SRC_FLAGS "-maltivec -mvsx")
set(MSA_SRC_FLAGS "-mmsa")

foreach(LIBVPX_SOURCE_FILE ${LIBVPX_SOURCES})
    get_filename_component(LIBVPX_SOURCE_NAME "${LIBVPX_SOURCE_FILE}" NAME_WE)
    get_filename_component(LIBVPX_SOURCE_EXT "${LIBVPX_SOURCE_FILE}" EXT)
    get_filename_component(LIBVPX_SOURCE_DIR "${LIBVPX_SOURCE_FILE}" DIRECTORY)
    if(LIBVPX_SOURCE_EXT STREQUAL ".c")
        if(LIBVPX_SOURCE_NAME MATCHES "_mmx$|_sse2$|_sse3$|_ssse3$|_sse4$|_avx$|_avx2$|_avx512$|_vsx$|_msa$")
            string(REGEX REPLACE "^.*_(.*)$" "\\1" VPX_SRC_SUFFIX "${LIBVPX_SOURCE_NAME}")
            string(TOUPPER ${VPX_SRC_SUFFIX} VPX_SRC_SUFFIX)
            set(VPX_SRC_FLAGS "${${VPX_SRC_SUFFIX}_SRC_FLAGS}")
            set_source_files_properties("${LIBVPX_SOURCE_FILE}" PROPERTIES COMPILE_FLAGS "${VPX_SRC_FLAGS}")
        endif()
    elseif(LIBVPX_SOURCE_EXT STREQUAL ".asm.S")
        set(LIBVPX_INPUT_FILE "${LIBVPX_SOURCE_DIR}/${LIBVPX_SOURCE_NAME}.asm")
        set(LIBVPX_OUTPUT_FILE "${LIBVPX_SOURCE_DIR}/${LIBVPX_SOURCE_NAME}.asm.S")
        asm_generate(INPUT ${LIBVPX_INPUT_FILE} OUTPUT ${LIBVPX_OUTPUT_FILE})
    endif()
endforeach()

add_library(vpx ${LIBVPX_SOURCES})

# installation

install(TARGETS vpx)

install(FILES ${LIBVPX_HEADERS}
    DESTINATION "include/vpx")

# pkg-config file

if(INSTALL_PKG_CONFIG_FILE)
    set(PC_LIBS "-lvpx -lm")
    set(PC_PRIVATE_LIBS "-lm")

    if(HAVE_PTHREAD_H)
        set(PC_PRIVATE_LIBS "${PC_PRIVATE_LIBS} -lpthread")
    endif()

    configure_file("${LIBVPX_SRC_DIR}/vpx.pc.in"
        "${LIBVPX_BIN_DIR}/vpx.pc" @ONLY)

    install(FILES "${LIBVPX_BIN_DIR}/vpx.pc"
        DESTINATION "lib/pkgconfig")
endif()
