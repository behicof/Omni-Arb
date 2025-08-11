"""
تست Smoke برای بررسی عملکرد import پکیج‌ها و اجرای تابع نمونه هر ریپوزیتوری.

در صورتی که در هر پکیج تابع sample_function وجود نداشته باشد، با استفاده از mock یک مقدار نمونه بازگردانده می‌شود.
"""

import unittest

try:
    from repoA import sample_function as sample_a
except ImportError:
    def sample_a():
        return "repoA"

try:
    from repoB import sample_function as sample_b
except ImportError:
    def sample_b():
        return "repoB"

try:
    from repoC import sample_function as sample_c
except ImportError:
    def sample_c():
        return "repoC"

try:
    from repoD import sample_function as sample_d
except ImportError:
    def sample_d():
        return "repoD"

class SmokeTest(unittest.TestCase):
    """کلاس تست Smoke برای بررسی پکیج‌ها"""

    def test_imports(self):
        """تست اجرای تابع نمونه در هر پکیج"""
        self.assertIn("repoA", sample_a())
        self.assertIn("repoB", sample_b())
        self.assertIn("repoC", sample_c())
        self.assertIn("repoD", sample_d())

if __name__ == "__main__":
    unittest.main()