from agent_recovery.benchmark_report import run_benchmark_report


def test_benchmark_report_covers_contract_without_inventing_metrics() -> None:
    report = run_benchmark_report()

    assert report.contract_coverage["covered_count"] == 10
    assert report.contract_coverage["required_count"] == 10
    assert report.contract_coverage["coverage_rate"] == 1.0

    metrics = report.metric_vector
    assert metrics["containment_success_rate_measured_scenarios"] == 1.0
    assert metrics["blast_radius_recall_b06"] == 1.0
    assert metrics["blast_radius_precision_b06"] == 1.0
    assert metrics["replay_attack_success_rate_measured_scenarios"] == 0.0
    assert metrics["residual_effect_truth_pass_rate_measured_scenarios"] == 1.0
    assert metrics["unsafe_recovery_executions"] == 0
    assert metrics["authority_resurrection_successes"] == 0

    assert "false_positive_containment_rate" in report.unmeasured_metrics
    assert "unsafe_recovery_action_rate_denominator" in report.unmeasured_metrics
