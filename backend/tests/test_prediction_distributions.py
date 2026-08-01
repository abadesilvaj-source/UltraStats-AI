from app.services.operational_pipeline_service import OperationalPipelineService


def test_negative_binomial_tail_is_bounded_and_monotonic() -> None:
    low_line = OperationalPipelineService._negative_binomial_over(
        4, 8.5, dispersion=6
    )
    high_line = OperationalPipelineService._negative_binomial_over(
        10, 8.5, dispersion=6
    )
    assert 0.02 <= high_line < low_line <= 0.98


def test_negative_binomial_handles_small_rate() -> None:
    probability = OperationalPipelineService._negative_binomial_over(
        3, .5, dispersion=4
    )
    assert 0.02 <= probability <= 0.98
