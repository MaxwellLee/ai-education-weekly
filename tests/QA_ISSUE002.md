# Issue 002 interface QA

Checked 2026-10-12, using the completed private build.

- Static checks passed for real issues 001 and 002. Latest issue is 002.
- Issue 002: 12 education records, 10 distinct public figures, 6 Shenzhen records.
- Cumulative ideas: 27, including 12 first included in issue 002.
- All 31 embedded image elements, including inert historical templates, decoded successfully. Repeated template image elements are not unique pictures.
- Every issue has five sections. Active HTML IDs are unique; cross-issue internal article routes resolve.
- All topic-by-stage matrix rows count each education record once.
- Pure state tests and the actual production controller in a synthetic DOM pass: previous/next/latest, five views, cumulative library, per-issue new filters, empty/reset, history navigation, return to issue 001 and its prior page.
- Both issue 001 JSON snapshot files are byte-identical to the pre-integration baseline.
- docs/index.html equals src/index.html.

## Limitations

The synthetic DOM verifies interaction logic but is not a rendering engine. Real-browser visual, mobile/touch, and cross-browser QA were not performed for this private build. Cloud Chrome responded, but no authorized private preview URL was available; no publishing was performed for testing, and the earlier file-URL access restriction was respected. This check does not independently reverify article facts or image permissions.

Run: python3 tests/check_static.py; node tests/test_core.js; node tests/test_dom.js.
The former single-issue hardcoded tests are retained under tests/archive_issue001 for reference, not as the current acceptance suite.
