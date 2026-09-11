#pragma once

#include <cstddef>
#include <string>
#include <string_view>

namespace vocotype::common {

// Keep UI-only streaming previews bounded without touching the full transcript.
// The ASR workers produce UTF-8, so walking continuation bytes is sufficient to
// preserve code-point boundaries for Chinese text and ordinary emoji.
[[nodiscard]] inline std::string
streaming_preview_tail(std::string_view text, std::size_t max_codepoints = 40) {
  if (text.empty() || max_codepoints == 0)
    return {};

  std::size_t codepoints = 0;
  for (const unsigned char byte : text) {
    if ((byte & 0xC0U) != 0x80U)
      ++codepoints;
  }
  if (codepoints <= max_codepoints)
    return std::string(text);

  std::size_t start = text.size();
  for (std::size_t kept = 0; kept < max_codepoints && start > 0; ++kept) {
    --start;
    while (start > 0 &&
           (static_cast<unsigned char>(text[start]) & 0xC0U) == 0x80U) {
      --start;
    }
  }
  return std::string("…") + std::string(text.substr(start));
}

} // namespace vocotype::common
