from pathlib import Path

import hydra
from omegaconf import DictConfig
import mlflow
import numpy as np
import optuna
from ray import tune
import wandb


def simulate_returns(params):
    rng = np.random.default_rng(42)
    return rng.normal(0, 1, 252)


def sharpe_ratio(returns: np.ndarray) -> float:
    return float(returns.mean() / returns.std())


def max_drawdown(returns: np.ndarray) -> float:
    cumulative = np.cumsum(returns)
    peak = np.maximum.accumulate(cumulative)
    drawdown = cumulative - peak
    return float(drawdown.min())


def evaluate(params):
    returns = simulate_returns(params)
    sr = sharpe_ratio(returns)
    mdd = max_drawdown(returns)
    return sr, mdd


def make_optuna_objective(cfg: DictConfig):
    def _objective(trial: optuna.Trial) -> float:
        params = {
            name: trial.suggest_float(name, space.low, space.high)
            for name, space in cfg.search_space.items()
        }
        sr, mdd = evaluate(params)
        trial.set_user_attr("max_dd", mdd)
        if abs(mdd) > cfg.constraint.max_dd:
            raise optuna.TrialPruned(f"MaxDD {mdd} exceeds {cfg.constraint.max_dd}")
        return sr

    return _objective


@hydra.main(config_path="conf", config_name="tune", version_base=None)
def main(cfg: DictConfig) -> float:
    mlflow.set_tracking_uri(cfg.mlflow.uri)
    mlflow.set_experiment(cfg.mlflow.experiment)
    wandb.init(project=cfg.wandb.project, mode="disabled")

    if cfg.optimizer == "optuna":
        study = optuna.create_study(direction="maximize", study_name=cfg.study_name)
        study.optimize(make_optuna_objective(cfg), n_trials=cfg.n_trials)
        best_trial = study.best_trial
        sr = best_trial.value
        mdd = best_trial.user_attrs.get("max_dd", 0.0)
    else:
        def tune_objective(config):
            sr, mdd = evaluate(config)
            tune.report(sharpe_oos=sr, max_dd=mdd)

        search_space = {
            name: tune.uniform(space.low, space.high)
            for name, space in cfg.search_space.items()
        }
        analysis = tune.run(
            tune_objective,
            config=search_space,
            num_samples=cfg.n_trials,
            metric="sharpe_oos",
            mode="max",
        )
        best_trial = analysis.get_best_trial(metric="sharpe_oos", mode="max")
        sr = best_trial.metric_analysis["sharpe_oos"]["max"]
        mdd = best_trial.metric_analysis["max_dd"]["max"]

    mlflow.log_metrics({"sharpe_oos": sr, "max_dd": mdd})
    wandb.log({"sharpe_oos": sr, "max_dd": mdd})

    exp_dir = Path(hydra.utils.get_original_cwd()) / "docs" / "experiments"
    exp_dir.mkdir(parents=True, exist_ok=True)
    card = exp_dir / f"{cfg.study_name}.md"
    with open(card, "w") as f:
        f.write(f"# {cfg.study_name}\n\n")
        f.write(f"- Optimizer: {cfg.optimizer}\n")
        f.write("- Objective: Sharpe_OOS\n")
        f.write(f"- Constraint: MaxDD <= {cfg.constraint.max_dd}\n")
        f.write(f"- Sharpe_OOS: {sr:.4f}\n")
        f.write(f"- MaxDD: {mdd:.4f}\n")

    print(f"Best Sharpe: {sr:.4f}, MaxDD: {mdd:.4f}")
    wandb.finish()
    return sr


if __name__ == "__main__":
    main()
