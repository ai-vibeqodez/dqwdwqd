cmake_minimum_required(VERSION 3.23)

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" RAW_VERSION)
string(STRIP "${RAW_VERSION}" PROJECT_VERSION)

project(app VERSION ${PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(app_lib STATIC
    src/math.cpp
)
target_include_directories(app_lib PUBLIC include)

add_executable(app
    src/main.cpp
)
target_link_libraries(app PRIVATE app_lib)

install(TARGETS app RUNTIME DESTINATION bin)

include(CTest)
if(BUILD_TESTING)
    include(FetchContent)
    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG        v3.7.1
    )
    FetchContent_MakeAvailable(Catch2)

    add_executable(unit_tests
        tests/test_math.cpp
    )
    target_link_libraries(unit_tests PRIVATE app_lib Catch2::Catch2WithMain)

    include(Catch)
    catch_discover_tests(unit_tests)
endif()
