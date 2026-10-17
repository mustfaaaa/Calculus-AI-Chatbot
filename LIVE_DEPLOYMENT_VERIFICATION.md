# Render preview verification — 2026-10-17

Target: https://calculus-ai-chatbot.onrender.com/

## Verified on the live deployment

- Home, lesson pages, solver and dashboard routes returned HTML; JS and CSS assets returned 200.
- `/health` returned 200. Unknown API and static-file paths returned 404.
- Saved-session/history routes returned 401 for guests, including a fake bearer token.
- Two independent JSON questions returned distinct primary/live Groq answers:
  derivative of `x**3` = `3*x**2`; derivative of `sin(x)` = `cos(x)`.
- A live SSE request completed with `done=true`, `mode=live`, `source=primary`.
- Browser product-rule question returned `2*x*sin(x) + x**2*cos(x)`.
  A follow-up asking for its value at zero retained the original function and returned zero.
- Switching lessons updated the chat topic. Rate limiting returned 429 and a visible chat-limit message.
- No warning/error console entries were captured in the tested browser session.

## Issues reproduced and corrected locally

- Valid `\cos\!\left(x\right)` notation was unparseable by the independent math
  checker. Normalize spacing and delimiter sizing; the previously captured live
  answers now both verify without additional model calls.
- Both public chat endpoints returned 500 for malformed JSON structures, such
  as an array body, null message or numeric context. Validate conversation and
  metadata types before processing or provider calls; return 400. Invalid input
  does not consume the chat-message allowance. Regression tests cover both routes.
- At a narrow mobile width, New Chat text overflowed its icon-width button and
  the floating close bubble covered the input area. Correct button sizing and
  hide the redundant floating close control while the mobile panel is open.
  Checked desktop and 320-pixel layouts in the browser; the header close button remains available.

Validation after corrections: 131 Python tests passed; 20 frontend tests passed;
production build compiled successfully. These include deterministic provider
timeouts, partial-stream failures, incomplete output, caching and frontend errors.

## Limits of this verification

One earlier live stream failed, then a retry succeeded. Its underlying provider
cause is unconfirmed because Render runtime logs are not available in this session.
The live 10-message/hour guest allowance was reached during testing; additional
provider questions were stopped. No quota or proxy protections were bypassed.

This is a guest preview, with demo lesson pages and no real login or durable
authenticated history. HTML fallback on a nonexistent `.env` URL is the app shell,
not evidence of a secret file being served. Tests do not establish correctness
for every possible calculus question or validate free-host cold starts.

Raw test reports are ignored under `test-results/`; browser screenshots are
local under `.cache/`. Live rollout of the corrections must be checked separately.
