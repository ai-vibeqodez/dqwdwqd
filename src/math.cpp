#include "app/math.hpp"

#include <stdexcept>

namespace app {

int divide(int a, int b) {
    if (b == 0) {
        throw std::invalid_argument("Division by zero");
    }
    return a / b;
}

} // namespace app
