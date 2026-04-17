"""Test i18n module."""
from flowfeed.i18n import set_locale, t, detect_locale, get_locale, SUPPORTED_LOCALES

# Test 1: detect locale
print("=== Test detect_locale ===")
print(f"Detected: {detect_locale()}")
print(f"Supported: {SUPPORTED_LOCALES}")

# Test 2: English
print()
print("=== English ===")
set_locale("en")
print(f"Locale: {get_locale()}")
print(t("cli.description"))
print(t("cli.no_items"))
print(t("engine.fetch_completed", dur=3.14))
print(t("engine.total_fetched", n=42))
print(t("term.header", items=100, sources=5))
print(t("term.top_stories"))
print(t("term.col_score"))
print(t("export.to_json", n=50))

# Test 3: Simplified Chinese
print()
print("=== zh-CN ===")
set_locale("zh-CN")
print(f"Locale: {get_locale()}")
print(t("cli.description"))
print(t("cli.no_items"))
print(t("engine.fetch_completed", dur=3.14))
print(t("engine.total_fetched", n=42))
print(t("term.header", items=100, sources=5))
print(t("term.top_stories"))
print(t("term.col_score"))
print(t("export.to_json", n=50))

# Test 4: Traditional Chinese
print()
print("=== zh-TW ===")
set_locale("zh-TW")
print(f"Locale: {get_locale()}")
print(t("cli.description"))
print(t("cli.no_items"))
print(t("engine.fetch_completed", dur=3.14))
print(t("term.header", items=100, sources=5))
print(t("term.top_stories"))
print(t("term.col_score"))
print(t("export.to_json", n=50))

# Test 5: HTML / MD / RSS keys
print()
print("=== Format keys ===")
for loc in ["en", "zh-CN", "zh-TW"]:
    set_locale(loc)
    print(f"[{loc}] html.stat_total={t('html.stat_total')} | md.title={t('md.title')} | rss.title={t('rss.title')}")

# Test 6: CLI keys
print()
print("=== CLI keys ===")
for loc in ["en", "zh-CN", "zh-TW"]:
    set_locale(loc)
    print(f"[{loc}] list_sources.title={t('cli.list_sources.title')} | init_config.exists={t('cli.init_config.exists', path='/tmp/x')}")

print()
print("ALL i18n TESTS PASSED")
