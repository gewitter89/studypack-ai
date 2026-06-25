import logging
from typing import Dict, Any, Tuple

from core.editorial_pass import editorial_pass
from core.quality_gate import run_quality_gate, compute_commercial_score

logger = logging.getLogger(__name__)


def postprocess(pack_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Post-processing: editorial pass + quality gate")
    edited = editorial_pass(pack_data)
    passed, hard_fails, warnings, commercial_fails, commercial_score = run_quality_gate(edited)
    all_errors = hard_fails + commercial_fails
    edited["_quality"] = {
        "passed": passed,
        "errors": all_errors,
        "warnings": warnings,
        "commercial_score": commercial_score,
        "hard_fails": hard_fails,
        "commercial_fails": commercial_fails,
    }
    if hard_fails:
        logger.warning(f"Quality gate HARD FAIL: {hard_fails}")
    if commercial_fails:
        logger.info(f"Quality gate COMMERCIAL: {commercial_fails}")
    if warnings:
        logger.info(f"Quality gate WARNINGS: {warnings}")
    return edited
