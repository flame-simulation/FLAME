cmake_minimum_required(VERSION 3.18)

project("flame" C CXX)

include(CTest)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(USE_WERROR "Treat warnings as errors" OFF)
option(USE_PYTHON "Build python support" ON)
option(USE_HDF5 "HDF5 output support" OFF)
option(NEED_PYTHON "Require python support" OFF)
option(USE_EPICS "Build EPICS virtual accelerator support" OFF)
option(NEED_EPICS  "Require EPICS support" OFF)
option(NEED_DEMOIOC  "build flamedemo IOC executable" OFF)

message(STATUS "Option PYTHON ${USE_PYTHON}")
message(STATUS "Option HDF5 ${USE_HDF5}")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
  message(STATUS "Default to Release build")
endif()

if(CMAKE_COMPILER_IS_GNUCC)
  # Turn on extra GCC warnings
  add_definitions(-Wall -Wextra)
  add_definitions(-Wno-unused-parameter -Wno-missing-field-initializers -Wno-cast-function-type)
  if(USE_WERROR)
    add_definitions(-Werror)
  endif()
endif()
message(STATUS "Build type ${CMAKE_BUILD_TYPE}")

#Default path for rf cavity data
if(DEF_PATH)
  add_definitions(-DDEFPATH=\"${DEF_PATH}\")
  message(STATUS "Set default rf cavity data path: ${DEF_PATH}")
endif()

# see if git submodule is actually checked out
if(USE_EPICS AND EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/cmake4epics/cmake/FindEPICS.cmake)
  list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake4epics/cmake)
  set(TRY_EPICS 1)
endif()

set(_boost_components
  filesystem
  program_options
)
if(BUILD_TESTING)
  list(APPEND _boost_components prg_exec_monitor unit_test_framework)
endif()
find_package(Boost 1.52.0 REQUIRED COMPONENTS ${_boost_components})

# respects -DHDF5_USE_STATIC_LIBRARIES=YES
# and environment variable HDF5_ROOT
if(USE_HDF5)
  find_package(HDF5 REQUIRED COMPONENTS C CXX)
  add_definitions(-DUSE_HDF5)
endif()

find_program(LEX_EXECUTABLE NAMES flex win_flex
  DOC "Location of lexer genereator"
)
find_program(YACC_EXECUTABLE NAMES bison win_bison
  DOC "Location of parser generator"
)
message(STATUS "FLEX ${LEX_EXECUTABLE}")
message(STATUS "BISON ${YACC_EXECUTABLE}")

if(NOT LEX_EXECUTABLE OR NOT YACC_EXECUTABLE)
  message(SEND_ERROR "Missing flex or bison")
endif()

find_program(CPPCHECK_EXECUTABLE cppcheck
  DOC "cppcheck executable"
)
message(STATUS "cppcheck ${CPPCHECK_EXECUTABLE}")

message(STATUS "Boost libs in ${Boost_LIBRARY_DIRS}")

if(USE_PYTHON)
  find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter Development.Module NumPy)
  message(STATUS "Python version ${Python3_VERSION}")
  message(STATUS "Python headers ${Python3_INCLUDE_DIRS}")
  message(STATUS "NumPy headers ${Python3_NumPy_INCLUDE_DIRS}")
endif()

if(USE_PYTHON AND BUILD_TESTING)
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -m pytest --version
    OUTPUT_QUIET
    ERROR_QUIET
    RESULT_VARIABLE _HAVE_PYTEST
  )
  if(_HAVE_PYTEST EQUAL 0)
    set(HAVE_PYTEST YES)
  else()
    set(HAVE_PYTEST NO)
    message(STATUS "Can't find pytest, not running Python tests")
  endif()
endif()

find_package(Doxygen)

if(TRY_EPICS)
  find_package(EPICS COMPONENTS IOC)
  find_package(EPICSTools)
endif()

add_subdirectory(src)
add_subdirectory(examples)

if(USE_PYTHON)
  message(STATUS "Building python support")
  add_subdirectory(python/flame)
elseif(NEED_PYTHON)
  message(SEND_ERROR "Unable to build Python support")
else()
  message(STATUS "Omitting python support")
endif()

add_subdirectory(tools)

if(EPICS_FOUND AND EPICSTOOLS_FOUND)
  message(STATUS "Building virtual accelerator IOC")
  add_subdirectory(vaccel)
elseif(NEED_EPICS)
  message(SEND_ERROR "Unable to build virtual accelerator IOC")
else()
  message(STATUS "Omit virtual accelerator IOC")
endif()

if(DOXYGEN_FOUND)
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/documentation)
  configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/documentation/Doxyfile.in
    ${CMAKE_CURRENT_BINARY_DIR}/documentation/Doxyfile
    @ONLY
  )
  add_custom_target(doc
    COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/documentation
  )
  if(UNIX)
    add_custom_target(doc-commit
      DEPENDS doc
      COMMAND find . -type f -print0 | xargs -0 ${CMAKE_CURRENT_SOURCE_DIR}/documentation/commit-gh.sh ${CMAKE_CURRENT_SOURCE_DIR}/.git
      WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/documentation/html
    )
  endif()
  message(STATUS "Will generate documentation")
else()
  message(STATUS "Skipping documentation generation (missing doxygen)")
endif()

if(CPPCHECK_EXECUTABLE)
  # Add a target with --enable=all for maximum noise for developers
  add_custom_target(cppcheck
    COMMAND ${CPPCHECK_EXECUTABLE} --enable=all --error-exitcode=1
                -I ${CMAKE_CURRENT_SOURCE_DIR}/src
                -I ${CMAKE_CURRENT_BINARY_DIR}/src
                -I ${CMAKE_CURRENT_BINARY_DIR}/python/flame
                ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
                ${CMAKE_CURRENT_BINARY_DIR}/src/*.c
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/cli.cpp
                ${CMAKE_CURRENT_SOURCE_DIR}/python/flame/mod*.cpp
    COMMENT "Running cppcheck static analysis"
  )
  # add a test with fewer checks (those which actually pass)
  add_test(NAME run_cppcheck
    COMMAND ${CPPCHECK_EXECUTABLE} --enable=performance,portability --error-exitcode=1
                -I ${CMAKE_CURRENT_SOURCE_DIR}/src
                -I ${CMAKE_CURRENT_BINARY_DIR}/src
                -I ${CMAKE_CURRENT_BINARY_DIR}/python/flame
                ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
                ${CMAKE_CURRENT_BINARY_DIR}/src/*.c
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/cli.cpp
                ${CMAKE_CURRENT_SOURCE_DIR}/python/flame/mod*.cpp
  )
endif()
