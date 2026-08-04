"""Diagnostic script - run this instead of main.py to check what's actually loaded."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("1) Project root:", os.path.dirname(os.path.abspath(__file__)))
print("=" * 60)

import utils.theme as theme
print("2) theme.py loaded from:", theme.__file__)
print("   BG_APP        =", theme.BG_APP)
print("   BG_CARD       =", theme.BG_CARD)
print("   TEXT_PRIMARY  =", theme.TEXT_PRIMARY)
print("   TEXT_BODY     =", theme.TEXT_BODY)
print("   PRIMARY       =", theme.PRIMARY)

print("=" * 60)
import views.styles as styles
print("3) styles.py loaded from:", styles.__file__)
print("   APP_STYLE type:", type(styles.APP_STYLE))
print("   APP_STYLE length:", len(styles.APP_STYLE))
print("   First 300 chars of APP_STYLE:")
print(styles.APP_STYLE[:300])
print("   ...")
print("   Does APP_STYLE still contain literal '{TEXT_BODY}' unresolved?",
      "{TEXT_BODY}" in styles.APP_STYLE)
print("   Does APP_STYLE still contain literal '{{' (double brace)?",
      "{{" in styles.APP_STYLE)

print("=" * 60)
import views.base_view as base_view
print("4) base_view.py loaded from:", base_view.__file__)
print("   STATUS_BG =", base_view.STATUS_BG)

print("=" * 60)
print("5) __pycache__ folders found:")
for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
    if "__pycache__" in root:
        print("  ", root)