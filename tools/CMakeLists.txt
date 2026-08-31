include_directories(
  ${Boost_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

add_executable(flamecli
  cli.cpp
)
target_link_libraries(flamecli
  flame_core
  Boost::program_options
)
set_target_properties(flamecli
  PROPERTIES
    OUTPUT_NAME flame
)
install(TARGETS flamecli
  RUNTIME DESTINATION bin
)
