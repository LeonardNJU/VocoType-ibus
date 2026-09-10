#pragma once

#include <memory>
#include <utility>

namespace vocotype::fcitx5 {

// Move the owner of the currently executing one-shot timer into callback-local
// storage. This clears the member immediately for nested cancellation or
// rescheduling, but defers destruction of the EventSource (and therefore the
// std::function closure that is executing) until the callback scope exits.
template <typename Timer>
[[nodiscard]] std::unique_ptr<Timer>
keepTimerAliveThroughCallback(std::unique_ptr<Timer> &owner) noexcept {
    return std::move(owner);
}

} // namespace vocotype::fcitx5
