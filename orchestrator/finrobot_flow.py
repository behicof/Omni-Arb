"""Simple orchestrator that evaluates funding edge and prints action."""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import yaml
from core.market_readers import snapshot


def main() -> None:
    with open("thresholds.yml") as f:
        thresholds = yaml.safe_load(f) or {}
    net = snapshot()
    if net >= thresholds.get("net_edge", 0):
        print("ENTER")
    else:
        print("SKIP")


if __name__ == "__main__":
    main()
