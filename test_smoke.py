"""تست Smoke برای بررسی عملکرد اولیه سیستم."""
import unittest

try:
    import sentiment_fingpt
except ImportError:  # pragma: no cover - handled in tests
    sentiment_fingpt = None

try:
    from rl import env as rl_env
except ImportError:  # pragma: no cover
    rl_env = None

try:
    import engine
except ImportError:  # pragma: no cover
    engine = None


class SmokeTest(unittest.TestCase):
    """کلاس تست Smoke جهت بررسی عملکرد پایه سیستم"""

    def test_imports(self):
        """تست import بخش‌های اصلی پروژه"""
        self.assertIsNotNone(sentiment_fingpt, "ماژول sentiment_fingpt باید موجود باشد")
        self.assertIsNotNone(rl_env, "ماژول rl.env باید موجود باشد")
        self.assertIsNotNone(engine, "ماژول engine باید موجود باشد")


if __name__ == "__main__":
    unittest.main()
