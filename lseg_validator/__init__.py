"""
lseg_validator — data quality toolkit for LSEG Data Library outputs.

Public API:
    DataQualityReport  — main entry point; composes all check modules.

Example::

    from lseg_validator import DataQualityReport
    report = DataQualityReport(df)
    report.summary()
    report.to_dict()
"""

from lseg_validator.report import DataQualityReport

__all__ = ["DataQualityReport"]
