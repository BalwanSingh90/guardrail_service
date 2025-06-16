"""
Evaluation Results Processing Module

This module processes and evaluates the results of compliance checks against ground truth data.
It computes various metrics including grade accuracy, summarization matching, and compliance
concern detection. The results are saved both per-case and as aggregate metrics.

The module handles:
1. Loading and validating test cases and raw responses
2. Computing evaluation metrics
3. Saving detailed and summary results
4. Error handling and logging
"""

import json
from dataclasses import dataclass
from glob import glob
from statistics import mean
from typing import Any, Dict, List

from app.core.config import Settings
from app.core.logging import get_logger

# Initialize logger and settings
logger = get_logger(__name__)
settings = Settings()

# Get evaluation paths from settings
paths = settings.get_evaluation_paths()

@dataclass
class EvaluationMetrics:
    """Data class to hold evaluation metrics for a single test case."""
    case_id: str
    grade_error: float
    summarization_match: bool
    concern_match: bool
    mitigation_match: bool
    overall_pass: bool

def load_test_cases() -> Dict[str, Dict[str, Any]]:
    """
    Load and validate test cases from the input file.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of test cases keyed by ID

    Raises:
        FileNotFoundError: If test cases file doesn't exist
        json.JSONDecodeError: If test cases file is invalid JSON
        ValueError: If test cases data is invalid
    """
    try:
        test_cases_path = paths["test_cases"]
        if not test_cases_path.exists():
            raise FileNotFoundError(f"Test cases file not found: {test_cases_path}")

        with open(test_cases_path) as f:
            cases = json.load(f)

        if not isinstance(cases, list):
            raise ValueError("Test cases must be a list")

        # Convert to dictionary and validate each case
        test_cases = {}
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError("Each test case must be a dictionary")
            if "id" not in case:
                raise ValueError("Each test case must have an 'id' field")
            if "ground_truth" not in case:
                raise ValueError(f"Test case {case['id']} missing 'ground_truth' field")

            test_cases[case["id"]] = case

        logger.info(f"Successfully loaded {len(test_cases)} test cases")
        return test_cases

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test cases file: {e!s}")
        raise
    except Exception as e:
        logger.error(f"Error loading test cases: {e!s}")
        raise

def parse_grade(grade_str: str) -> float:
    """
    Parse a grade string into a float value.

    Args:
        grade_str: Grade string in format "X/Y"

    Returns:
        float: Parsed grade value

    Raises:
        ValueError: If grade string is invalid
    """
    try:
        return float(grade_str.split("/")[0])
    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid grade format: {grade_str}") from e

def evaluate_response(
    case_id: str,
    ground_truth: Dict[str, Any],
    response: Dict[str, Any]
) -> EvaluationMetrics:
    """
    Evaluate a single response against its ground truth.

    Args:
        case_id: Test case identifier
        ground_truth: Ground truth data
        response: Response data to evaluate

    Returns:
        EvaluationMetrics: Computed evaluation metrics

    Raises:
        ValueError: If response data is invalid
    """
    try:
        # Compute grade error
        gt_grade = parse_grade(ground_truth["grade"])
        resp_grade = parse_grade(response["grade"])
        grade_error = abs(gt_grade - resp_grade)

        # Compute matches
        summarization_match = (
            ground_truth["summarization"].strip() ==
            response["summarization"].strip()
        )
        concern_match = (
            ground_truth["critical_compliance_concern"] ==
            response.get("critical_compliance_concern", "")
        )
        mitigation_match = (
            ground_truth["required_mitigation"] ==
            response.get("required_mitigation", "")
        )

        # Determine overall pass using configured tolerance
        overall_pass = (
            summarization_match and
            abs(grade_error) < settings.evaluation_grade_tolerance and
            concern_match and
            mitigation_match
        )

        return EvaluationMetrics(
            case_id=case_id,
            grade_error=grade_error,
            summarization_match=summarization_match,
            concern_match=concern_match,
            mitigation_match=mitigation_match,
            overall_pass=overall_pass
        )

    except Exception as e:
        logger.error(f"Error evaluating response for case {case_id}: {e!s}")
        raise ValueError(f"Invalid response data for case {case_id}") from e

def save_evaluation_metrics(metrics: EvaluationMetrics) -> None:
    """
    Save evaluation metrics for a single test case.

    Args:
        metrics: Evaluation metrics to save
    """
    try:
        output_file = paths["evaluated"] / f"{metrics.case_id}_eval.json"
        with open(output_file, "w") as f:
            json.dump(metrics.__dict__, f, indent=2)
        logger.debug(f"Saved evaluation metrics for case {metrics.case_id}")
    except Exception as e:
        logger.error(f"Error saving metrics for case {metrics.case_id}: {e!s}")
        raise

def compute_summary_metrics(metrics_list: List[EvaluationMetrics]) -> Dict[str, Any]:
    """
    Compute summary metrics from individual evaluation results.

    Args:
        metrics_list: List of evaluation metrics

    Returns:
        Dict[str, Any]: Summary metrics
    """
    try:
        return {
            "total_tests": len(metrics_list),
            "pass_rate": sum(m.overall_pass for m in metrics_list) / len(metrics_list),
            "avg_grade_error": mean(m.grade_error for m in metrics_list),
            "summarization_match_rate": sum(m.summarization_match for m in metrics_list) / len(metrics_list),
            "concern_match_rate": sum(m.concern_match for m in metrics_list) / len(metrics_list),
            "mitigation_match_rate": sum(m.mitigation_match for m in metrics_list) / len(metrics_list),
            "grade_tolerance": settings.evaluation_grade_tolerance
        }
    except Exception as e:
        logger.error(f"Error computing summary metrics: {e!s}")
        raise

def main() -> None:
    """Main evaluation process."""
    try:
        logger.info("Starting evaluation process")
        logger.info(f"Using evaluation directory: {paths['base']}")

        # Load test cases
        test_cases = load_test_cases()

        # Process each raw response file
        results = []
        raw_responses_dir = paths["raw_responses"]
        for raw_file in glob(str(raw_responses_dir / "*.json")):
            try:
                with open(raw_file) as f:
                    data = json.load(f)

                case_id = data["id"]
                if case_id not in test_cases:
                    logger.warning(f"Unknown test case ID in response: {case_id}")
                    continue

                # Evaluate response
                metrics = evaluate_response(
                    case_id=case_id,
                    ground_truth=test_cases[case_id]["ground_truth"],
                    response=data["response"]
                )

                # Save individual metrics
                save_evaluation_metrics(metrics)
                results.append(metrics)

            except Exception as e:
                logger.error(f"Error processing file {raw_file}: {e!s}")
                continue

        if not results:
            raise ValueError("No valid results to evaluate")

        # Compute and save summary metrics
        summary = compute_summary_metrics(results)
        with open(paths["metrics_file"], "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Evaluation complete. Processed {len(results)} test cases")
        logger.info(f"Summary metrics written to {paths['metrics_file']}")
        logger.info(f"Pass rate: {summary['pass_rate']:.2%}")
        logger.info(f"Grade tolerance: {settings.evaluation_grade_tolerance}")

    except Exception as e:
        logger.error(f"Evaluation process failed: {e!s}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
