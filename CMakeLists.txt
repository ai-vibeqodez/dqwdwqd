cmake_minimum_required(VERSION 3.23)

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" RAW_VERSION)
string(STRIP "${RAW_VERSION}" PROJECT_VERSION)

project(app VERSION ${PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(APP_ENABLE_WARNINGS "Enable strict compiler warnings for app targets" OFF)
option(APP_WARNINGS_AS_ERRORS "Treat app target warnings as errors" OFF)

function(app_enable_warnings target)
    if(NOT APP_ENABLE_WARNINGS)
        return()
    endif()

    if(MSVC)
        target_compile_options(${target} PRIVATE /W4)
        if(APP_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE /WX)
        endif()
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion)
        if(APP_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE -Werror)
        endif()
    endif()
endfunction()

add_library(app_lib STATIC
    src/math.cpp
)
target_include_directories(app_lib PUBLIC include)
app_enable_warnings(app_lib)

add_executable(app
    src/main.cpp
)
target_link_libraries(app PRIVATE app_lib)
app_enable_warnings(app)

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
    app_enable_warnings(unit_tests)

    include(Catch)
    catch_discover_tests(unit_tests)
endif()
