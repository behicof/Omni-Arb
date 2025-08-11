"""
ماژول اصلی برنامه.

این اسکریپت ۴ پکیج (repoA, repoB, repoC, repoD) را import کرده و نسخه یا خلاصه‌ای از آن‌ها را چاپ می‌کند.
"""

from repoA import __version__ as version_a, summary as summary_a
from repoB import __version__ as version_b, summary as summary_b
from repoC import __version__ as version_c, summary as summary_c
from repoD import __version__ as version_d, summary as summary_d

def main() -> None:
    """
    تابع اصلی برنامه که نسخه و خلاصه پکیج‌ها را چاپ می‌کند.
    """
    print("نسخه و خلاصه هر پکیج:")
    print(f"repoA - نسخه: {version_a}, خلاصه: {summary_a}")
    print(f"repoB - نسخه: {version_b}, خلاصه: {summary_b}")
    print(f"repoC - نسخه: {version_c}, خلاصه: {summary_c}")
    print(f"repoD - نسخه: {version_d}, خلاصه: {summary_d}")

if __name__ == "__main__":
    main()