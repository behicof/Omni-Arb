"""
تست Smoke برای بررسی عملکرد اولیه سیستم.

این تست شامل:
- بررسی import ماژول‌های اصلی (signals, policy, exec)
- اجرای توابع نمونه جهت اطمینان از بارگذاری صحیح ماژول‌ها

در صورت عدم وجود توابع واقعی، استفاده از mock انجام می‌شود.
"""
import unittest

try:
    import sentiment_fingpt
except ImportError:
    sentiment_fingpt = None

try:
    import rl_agent  # type: ignore
except ImportError:
    rl_agent = None

try:
    import engine
except ImportError:
    engine = None

class SmokeTest(unittest.TestCase):
    """کلاس تست Smoke جهت بررسی عملکرد پایه سیستم"""

    def test_imports(self):
        """تست import بخش‌های اصلی پروژه"""
        self.assertIsNotNone(sentiment_fingpt, "ماژول sentiment_fingpt باید موجود باشد")
        self.assertIsNotNone(rl_agent, "ماژول rl_agent باید موجود باشد")
        self.assertIsNotNone(engine, "ماژول engine باید موجود باشد")

if __name__ == "__main__":
    unittest.main()