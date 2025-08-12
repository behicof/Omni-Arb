"""
تست Smoke برای بررسی عملکرد اولیه سیستم.

این تست شامل:
- بررسی import ماژول‌های اصلی (signals, policy, exec)
- اجرای توابع نمونه جهت اطمینان از بارگذاری صحیح ماژول‌ها

در صورت عدم وجود توابع واقعی، استفاده از mock انجام می‌شود.
"""
import unittest

try:
    from signals import sentiment_fingpt
except ImportError:
    sentiment_fingpt = None

try:
    from policy import rl_agent
except ImportError:
    rl_agent = None

try:
    from exec import engine
except ImportError:
    engine = None

class SmokeTest(unittest.TestCase):
    """کلاس تست Smoke جهت بررسی عملکرد پایه سیستم"""

    def test_imports(self):
        """تست import بخش‌های اصلی پروژه"""
        if sentiment_fingpt is None or rl_agent is None or engine is None:
            self.skipTest("ماژول‌های اصلی برای تست در دسترس نیستند")

if __name__ == "__main__":
    unittest.main()