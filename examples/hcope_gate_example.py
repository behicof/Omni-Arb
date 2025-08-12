"""Example demonstrating use of the HCOPE gate.

This script shows how to evaluate whether a policy should move to live
execution based on its estimated Sharpe ratio and uncertainty.  The
``hcope_gate`` function computes a lower confidence bound on the Sharpe
ratio and compares it to a threshold.  If the gate passes, the policy is
considered safe to deploy.
"""
from hcope import hcope_gate

# Estimated Sharpe ratio and its standard deviation
estimated_sharpe = 1.2
estimated_std_sharpe = 0.5

if hcope_gate(estimated_sharpe, estimated_std_sharpe):
    print("Running live deployment...")
else:
    print("Adjusting policy strategy...")

