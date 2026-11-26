#ifndef APP_MATH_HPP
#define APP_MATH_HPP

namespace app {

[[nodiscard]] constexpr int add(int a, int b) noexcept {
    return a + b;
}

[[nodiscard]] int divide(int a, int b);

} // namespace app

#endif // APP_MATH_HPP
