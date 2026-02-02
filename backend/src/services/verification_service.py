"""
Verification service for the verification system.
This module provides business logic for feature verification and tracking.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio
from enum import Enum

from ..models.feature import Feature, VerificationStatus, VerificationResult
from ..models.verification_report import VerificationReport
from ..models.user import User
from ..database.database import get_db
from ..utils.logging import get_logger


class VerificationError(Exception):
    """
    Custom exception for verification-related errors
    """
    pass


class VerificationMethod(Enum):
    """
    Different methods of verification
    """
    AUTOMATED = "automated"
    MANUAL = "manual"
    BOTH = "both"


class VerificationService:
    """
    Service class for handling feature verification logic
    """
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def get_all_features(self) -> List[Feature]:
        """
        Retrieve all features in the system.

        Returns:
            List[Feature]: List of all features
        """
        try:
            features = self.db.query(Feature).filter(Feature.is_active == True).all()
            self.logger.info(f"Retrieved {len(features)} features")
            return features
        except Exception as e:
            self.logger.error(f"Error retrieving features: {str(e)}")
            raise VerificationError(f"Failed to retrieve features: {str(e)}")

    def get_feature_by_id(self, feature_id: uuid.UUID) -> Optional[Feature]:
        """
        Retrieve a specific feature by ID.

        Args:
            feature_id: ID of the feature to retrieve

        Returns:
            Feature: The feature if found, None otherwise
        """
        try:
            feature = self.db.query(Feature).filter(
                Feature.id == feature_id,
                Feature.is_active == True
            ).first()

            if feature:
                self.logger.info(f"Retrieved feature {feature_id}")
            else:
                self.logger.info(f"Feature {feature_id} not found")

            return feature
        except Exception as e:
            self.logger.error(f"Error retrieving feature {feature_id}: {str(e)}")
            raise VerificationError(f"Failed to retrieve feature: {str(e)}")

    def get_verification_report_by_feature(self, feature_id: uuid.UUID) -> List[VerificationReport]:
        """
        Retrieve all verification reports for a specific feature.

        Args:
            feature_id: ID of the feature

        Returns:
            List[VerificationReport]: List of verification reports for the feature
        """
        try:
            reports = self.db.query(VerificationReport)\
                .filter(VerificationReport.feature_id == feature_id)\
                .order_by(VerificationReport.created_at.desc())\
                .all()

            self.logger.info(f"Retrieved {len(reports)} verification reports for feature {feature_id}")
            return reports
        except Exception as e:
            self.logger.error(f"Error retrieving verification reports for feature {feature_id}: {str(e)}")
            raise VerificationError(f"Failed to retrieve verification reports: {str(e)}")

    def get_latest_verification_report(self, feature_id: uuid.UUID) -> Optional[VerificationReport]:
        """
        Retrieve the latest verification report for a specific feature.

        Args:
            feature_id: ID of the feature

        Returns:
            VerificationReport: The latest verification report if found, None otherwise
        """
        try:
            report = self.db.query(VerificationReport)\
                .filter(VerificationReport.feature_id == feature_id)\
                .order_by(VerificationReport.created_at.desc())\
                .first()

            if report:
                self.logger.info(f"Retrieved latest verification report for feature {feature_id}")
            else:
                self.logger.info(f"No verification report found for feature {feature_id}")

            return report
        except Exception as e:
            self.logger.error(f"Error retrieving latest verification report for feature {feature_id}: {str(e)}")
            raise VerificationError(f"Failed to retrieve verification report: {str(e)}")

    def create_verification_report(
        self,
        feature_id: uuid.UUID,
        verification_type: str = "automated",
        status: VerificationStatus = VerificationStatus.PENDING
    ) -> VerificationReport:
        """
        Create a new verification report.

        Args:
            feature_id: ID of the feature to verify
            verification_type: Type of verification (automated, manual, both)
            status: Initial status of the verification

        Returns:
            VerificationReport: The created verification report
        """
        try:
            # Verify the feature exists
            feature = self.get_feature_by_id(feature_id)
            if not feature:
                raise VerificationError(f"Feature with ID {feature_id} does not exist")

            # Create the verification report
            verification_report = VerificationReport(
                feature_id=feature_id,
                verification_type=verification_type,
                status=status
            )

            self.db.add(verification_report)
            self.db.commit()
            self.db.refresh(verification_report)

            self.logger.info(f"Created verification report {verification_report.id} for feature {feature_id}")
            return verification_report
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating verification report for feature {feature_id}: {str(e)}")
            raise VerificationError(f"Failed to create verification report: {str(e)}")

    async def perform_verification(
        self,
        verification_report_id: uuid.UUID,
        verification_method: VerificationMethod = VerificationMethod.AUTOMATED
    ):
        """
        Perform the actual verification process.

        Args:
            verification_report_id: ID of the verification report to update
            verification_method: Method to use for verification
        """
        try:
            # Get the verification report
            report = self.db.query(VerificationReport)\
                .filter(VerificationReport.id == verification_report_id).first()

            if not report:
                self.logger.error(f"Verification report {verification_report_id} not found")
                return

            # Update status to in progress
            report.status = VerificationStatus.IN_PROGRESS
            report.updated_at = datetime.utcnow()
            self.db.commit()

            # Simulate verification process based on method
            await self._execute_verification_process(report, verification_method)

            # Update completion time
            report.completed_at = datetime.utcnow()
            report.updated_at = datetime.utcnow()
            self.db.commit()

            self.logger.info(f"Completed verification for report {verification_report_id}")

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error performing verification for report {verification_report_id}: {str(e)}")
            # Update the report with failure status
            try:
                report = self.db.query(VerificationReport)\
                    .filter(VerificationReport.id == verification_report_id).first()
                if report:
                    report.status = VerificationStatus.COMPLETE
                    report.result = VerificationResult.FAIL
                    report.findings = f"Verification failed: {str(e)}"
                    report.updated_at = datetime.utcnow()
                    self.db.commit()
            except Exception:
                pass  # If we can't update the status, there's nothing more we can do

    async def _execute_verification_process(
        self,
        report: VerificationReport,
        verification_method: VerificationMethod
    ):
        """
        Execute the actual verification process based on the method.

        Args:
            report: The verification report to update
            verification_method: Method to use for verification
        """
        try:
            # Simulate processing time
            await asyncio.sleep(2)  # Simulate some work

            # In a real implementation, this would perform actual verification
            # such as running tests, comparing against specifications, etc.

            if verification_method == VerificationMethod.AUTOMATED:
                # Simulate automated verification
                await self._perform_automated_verification(report)
            elif verification_method == VerificationMethod.MANUAL:
                # Simulate manual verification
                await self._perform_manual_verification(report)
            elif verification_method == VerificationMethod.BOTH:
                # Simulate both automated and manual verification
                await self._perform_automated_verification(report)
                await self._perform_manual_verification(report)

        except Exception as e:
            self.logger.error(f"Error in verification process: {str(e)}")
            raise

    async def _perform_automated_verification(self, report: VerificationReport):
        """
        Perform automated verification checks.

        Args:
            report: The verification report to update
        """
        try:
            # Simulate running automated tests
            self.logger.info(f"Performing automated verification for report {report.id}")

            # Simulate test results
            test_results = {
                "total_tests": 10,
                "passed_tests": 9,
                "failed_tests": 1,
                "skipped_tests": 0
            }

            # Determine result based on test results
            if test_results["failed_tests"] == 0:
                report.result = VerificationResult.PASS
                report.findings = f"Automated verification passed. All {test_results['total_tests']} tests passed."
                report.recommendations = ["No recommendations needed."]
            elif test_results["failed_tests"] <= 2:
                report.result = VerificationResult.NEEDS_WORK
                report.findings = f"Automated verification partially passed. {test_results['passed_tests']} passed, {test_results['failed_tests']} failed."
                report.recommendations = ["Fix the failing tests", "Review the failed test cases"]
            else:
                report.result = VerificationResult.FAIL
                report.findings = f"Automated verification failed. {test_results['passed_tests']} passed, {test_results['failed_tests']} failed."
                report.recommendations = ["Critical issues found. Address all failing tests before release."]

            # Update status to complete
            report.status = VerificationStatus.COMPLETE

            self.logger.info(f"Completed automated verification for report {report.id}")

        except Exception as e:
            self.logger.error(f"Error in automated verification: {str(e)}")
            raise

    async def _perform_manual_verification(self, report: VerificationReport):
        """
        Perform manual verification checks.

        Args:
            report: The verification report to update
        """
        try:
            # Simulate manual verification process
            self.logger.info(f"Performing manual verification for report {report.id}")

            # In a real implementation, this would involve manual review of the feature
            # against specifications, user acceptance testing, etc.

            # For simulation, we'll just add manual verification findings
            manual_findings = "Manual review completed. Feature meets specification requirements."
            manual_recommendations = ["Consider adding additional edge case tests"]

            # Append to existing findings and recommendations
            if report.findings:
                report.findings += f" {manual_findings}"
            else:
                report.findings = manual_findings

            if report.recommendations:
                report.recommendations += manual_recommendations
            else:
                report.recommendations = manual_recommendations

            # If result wasn't already set by automated verification, set it now
            if not report.result:
                report.result = VerificationResult.PASS

            # Update status to complete
            report.status = VerificationStatus.COMPLETE

            self.logger.info(f"Completed manual verification for report {report.id}")

        except Exception as e:
            self.logger.error(f"Error in manual verification: {str(e)}")
            raise

    def get_verification_statistics(self) -> dict:
        """
        Get verification statistics for the system.

        Returns:
            dict: Statistics about verification activities
        """
        try:
            # Count total features
            total_features = self.db.query(Feature).filter(Feature.is_active == True).count()

            # Count features with verification reports
            features_with_verifications = self.db.query(VerificationReport.feature_id).distinct().count()

            # Count verification reports by status
            verification_counts = {}
            for status in VerificationStatus:
                count = self.db.query(VerificationReport)\
                    .filter(VerificationReport.status == status).count()
                verification_counts[status.value] = count

            # Count verification results
            result_counts = {}
            for result in VerificationResult:
                count = self.db.query(VerificationReport)\
                    .filter(VerificationReport.result == result).count()
                result_counts[result.value if result else "none"] = count

            stats = {
                "total_features": total_features,
                "features_with_verifications": features_with_verifications,
                "verification_status_counts": verification_counts,
                "verification_result_counts": result_counts,
                "verification_coverage": round((features_with_verifications / total_features) * 100, 2) if total_features > 0 else 0
            }

            self.logger.info("Retrieved verification statistics")
            return stats

        except Exception as e:
            self.logger.error(f"Error retrieving verification statistics: {str(e)}")
            raise VerificationError(f"Failed to retrieve verification statistics: {str(e)}")

    def get_features_by_verification_result(self, result: VerificationResult) -> List[Feature]:
        """
        Get all features with a specific verification result.

        Args:
            result: The verification result to filter by

        Returns:
            List[Feature]: List of features with the specified verification result
        """
        try:
            # Get all features that have at least one verification report with the specified result
            feature_ids = self.db.query(VerificationReport.feature_id)\
                .filter(VerificationReport.result == result)\
                .distinct().all()

            feature_ids = [fid[0] for fid in feature_ids]

            features = self.db.query(Feature).filter(
                Feature.id.in_(feature_ids),
                Feature.is_active == True
            ).all()

            self.logger.info(f"Retrieved {len(features)} features with verification result {result.value}")
            return features

        except Exception as e:
            self.logger.error(f"Error retrieving features by verification result {result.value}: {str(e)}")
            raise VerificationError(f"Failed to retrieve features by verification result: {str(e)}")