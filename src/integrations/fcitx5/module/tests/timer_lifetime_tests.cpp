#include "../../common/timer_lifetime.hpp"

#include <fcitx-utils/event.h>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>

namespace {

struct Harness {
    fcitx::EventLoop loop;
    std::unique_ptr<fcitx::EventSourceTime> timer;
    int fired = 0;
    static constexpr int kTarget = 8;

    void schedule() {
        if (timer) {
            throw std::runtime_error("timer owner must be empty before reschedule");
        }
        timer = loop.addTimeEvent(
            CLOCK_MONOTONIC, fcitx::now(CLOCK_MONOTONIC) + 1000, 0,
            [this](fcitx::EventSourceTime *, uint64_t) {
                [[maybe_unused]] auto keepalive =
                    vocotype::fcitx5::keepTimerAliveThroughCallback(timer);

                if (timer) {
                    throw std::runtime_error(
                        "timer member was not cleared inside callback");
                }

                ++fired;
                // Exercise both capture access and same-callback rescheduling
                // after ownership has moved out of the member.
                if (fired < kTarget) {
                    schedule();
                } else {
                    loop.exit();
                }
                return false;
            });
        timer->setOneShot();
    }
};

} // namespace

int main() {
    try {
        Harness harness;
        harness.schedule();
        if (!harness.loop.exec()) {
            throw std::runtime_error("Fcitx event loop exited unsuccessfully");
        }
        if (harness.fired != Harness::kTarget) {
            throw std::runtime_error("timer did not fire expected number of times");
        }
        std::cout << "Fcitx timer lifetime test passed: " << harness.fired
                  << " callbacks\n";
        return EXIT_SUCCESS;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
