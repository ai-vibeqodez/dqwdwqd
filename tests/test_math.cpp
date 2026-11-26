#include "app/math.hpp"

#include <catch2/catch_test_macros.hpp>
#include <stdexcept>

TEST_CASE("math operations", "[math]") {
    REQUIRE(app::add(2, 3) == 5);
    REQUIRE(app::divide(10, 2) == 5);
    REQUIRE_THROWS_AS(app::divide(1, 0), std::invalid_argument);
}
