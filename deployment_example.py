"""Example live deployment gating using HCOPE."""
from hcope import hcope_gate

def maybe_deploy(estimated_sharpe: float, estimated_std_sharpe: float) -> None:
    """Run live deployment when the policy passes the HCOPE gate.

    Args:
        estimated_sharpe: Estimated Sharpe ratio for the policy.
        estimated_std_sharpe: Standard deviation of the Sharpe ratio estimate.
    """
    if hcope_gate(estimated_sharpe, estimated_std_sharpe):
        # Continue with Live Execution
        print("Running live deployment...")
    else:
        # Abort or Adjust Strategy
        print("Adjusting policy strategy...")


if __name__ == "__main__":
    # Example usage with placeholder metrics
    maybe_deploy(1.5, 0.2)
