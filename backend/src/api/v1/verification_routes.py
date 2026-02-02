"""
Verification API endpoints for the verification system.
This module provides endpoints for feature verification and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import asyncio

from ...database.database import get_db
from ...models.feature import Feature, VerificationStatus, VerificationResult
from ...models.verification_report import VerificationReport
from ...models.user import User
from ...middleware.auth import get_current_user
from ...middleware.error_handler import BusinessLogicError, NotFoundError
from ...services.verification_service import VerificationService
from ...utils.logging import get_logger


router = APIRouter(prefix="/verification", tags=["verification"])
logger = get_logger(__name__)


@router.get("/features", summary="Get All Features")
async def get_features(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve list of all features with their verification status.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of features with verification status
    """
    try:
        # Query all features with their verification status
        features = db.query(Feature).filter(Feature.is_active == True).all()

        features_list = []
        for feature in features:
            # Get the latest verification report for this feature
            latest_verification = db.query(VerificationReport)\
                .filter(VerificationReport.feature_id == feature.id)\
                .order_by(VerificationReport.created_at.desc())\
                .first()

            feature_dict = feature.to_dict()
            feature_dict["status"] = latest_verification.status.value if latest_verification else "pending"
            feature_dict["verification_result"] = latest_verification.result.value if latest_verification else None
            feature_dict["last_verified"] = latest_verification.completed_at.isoformat() if latest_verification and latest_verification.completed_at else None

            features_list.append(feature_dict)

        logger.info(f"Retrieved {len(features_list)} features for user {current_user.id}")

        return {
            "features": features_list
        }

    except Exception as e:
        logger.error(f"Error retrieving features: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/features/{feature_id}", summary="Get Feature Details")
async def get_feature_details(
    feature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get detailed verification information for a specific feature.

    Args:
        feature_id: ID of the feature to retrieve
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Detailed feature information with verification details
    """
    try:
        # Validate feature_id format
        try:
            feature_uuid = uuid.UUID(feature_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid feature ID format")

        # Get the feature
        feature = db.query(Feature).filter(Feature.id == feature_uuid, Feature.is_active == True).first()
        if not feature:
            raise NotFoundError("Feature", feature_id)

        # Get all verification reports for this feature
        verification_reports = db.query(VerificationReport)\
            .filter(VerificationReport.feature_id == feature.id)\
            .order_by(VerificationReport.created_at.desc())\
            .all()

        # Get the latest verification report
        latest_verification = verification_reports[0] if verification_reports else None

        # Prepare the response
        feature_dict = feature.to_dict()
        feature_dict["status"] = latest_verification.status.value if latest_verification else "pending"
        feature_dict["verification_result"] = latest_verification.result.value if latest_verification else None
        feature_dict["last_verified"] = latest_verification.completed_at.isoformat() if latest_verification and latest_verification.completed_at else None

        # Prepare detailed verification history
        verification_history = []
        for report in verification_reports:
            verification_history.append({
                "id": str(report.id),
                "verification_type": report.verification_type,
                "status": report.status.value,
                "result": report.result.value if report.result else None,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "created_at": report.created_at.isoformat(),
                "completed_at": report.completed_at.isoformat() if report.completed_at else None
            })

        feature_detail = {
            "feature": {
                "id": feature_dict["id"],
                "name": feature_dict["name"],
                "description": feature_dict["description"],
                "specification_reference": feature_dict["specification_reference"],
                "status": feature_dict["status"],
                "verification_result": feature_dict["verification_result"],
                "last_verified": feature_dict["last_verified"],
                "detailed_findings": latest_verification.findings if latest_verification else None,
                "test_results": [],  # This would be populated from actual test results in a real implementation
                "recommendations": latest_verification.recommendations if latest_verification else [],
                "verification_history": verification_history
            }
        }

        logger.info(f"Retrieved details for feature {feature_id} by user {current_user.id}")

        return feature_detail

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feature details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/features/{feature_id}/verify", summary="Initiate Feature Verification")
async def initiate_verification(
    feature_id: str,
    verification_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Initiate verification process for a specific feature.

    Args:
        feature_id: ID of the feature to verify
        verification_data: Verification parameters
        background_tasks: FastAPI background tasks
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Verification initiation response
    """
    try:
        # Validate feature_id format
        try:
            feature_uuid = uuid.UUID(feature_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid feature ID format")

        # Verify the feature exists
        feature = db.query(Feature).filter(Feature.id == feature_uuid, Feature.is_active == True).first()
        if not feature:
            raise NotFoundError("Feature", feature_id)

        # Validate verification data
        verification_type = verification_data.get("verification_type", "automated")
        if verification_type not in ["automated", "manual", "both"]:
            raise HTTPException(status_code=400, detail="verification_type must be 'automated', 'manual', or 'both'")

        # Create a new verification report record
        verification_report = VerificationReport(
            feature_id=feature.id,
            verification_type=verification_type,
            status=VerificationStatus.IN_PROGRESS
        )
        db.add(verification_report)
        db.commit()
        db.refresh(verification_report)

        # Schedule the verification process as a background task
        # In a real implementation, this would perform the actual verification
        background_tasks.add_task(
            perform_verification_task,
            verification_report.id,
            feature.id,
            verification_type,
            db
        )

        response = {
            "verification_id": str(verification_report.id),
            "status": "in_progress",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()  # Estimate 5 minutes
        }

        logger.info(f"Started verification for feature {feature_id} (verification_id: {verification_report.id}) by user {current_user.id}")

        return response

    except NotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def perform_verification_task(
    verification_report_id: uuid.UUID,
    feature_id: uuid.UUID,
    verification_type: str,
    db_session: Session
):
    """
    Background task to perform the actual verification.

    Args:
        verification_report_id: ID of the verification report
        feature_id: ID of the feature to verify
        verification_type: Type of verification to perform
        db_session: Database session for this task
    """
    try:
        # Get a new database session for this background task
        from ...database.database import SessionLocal
        db = SessionLocal()

        try:
            # Get the verification report
            verification_report = db.query(VerificationReport)\
                .filter(VerificationReport.id == verification_report_id).first()

            if not verification_report:
                logger.error(f"Verification report {verification_report_id} not found")
                return

            # Simulate verification process
            # In a real implementation, this would perform actual verification
            # such as running tests, comparing against specifications, etc.

            # For simulation purposes, we'll just sleep briefly
            await asyncio.sleep(2)  # Simulate some processing time

            # Update the verification report with results
            # For this example, we'll simulate a successful verification
            verification_report.status = VerificationStatus.COMPLETE
            verification_report.result = VerificationResult.PASS
            verification_report.findings = "Verification completed successfully. All requirements met."
            verification_report.recommendations = ["No recommendations needed."]
            verification_report.completed_at = datetime.utcnow()

            db.commit()

            logger.info(f"Completed verification for feature {feature_id} (report: {verification_report_id})")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in verification background task: {str(e)}")

        # Try to update the verification report with failure status
        try:
            from ...database.database import SessionLocal
            db = SessionLocal()

            verification_report = db.query(VerificationReport)\
                .filter(VerificationReport.id == verification_report_id).first()

            if verification_report:
                verification_report.status = VerificationStatus.COMPLETE
                verification_report.result = VerificationResult.FAIL
                verification_report.findings = f"Verification failed: {str(e)}"
                verification_report.completed_at = datetime.utcnow()

                db.commit()

            db.close()
        except Exception:
            pass  # If we can't update the status, there's nothing more we can do


@router.get("/reports", summary="Get Verification Reports")
async def get_verification_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve list of verification reports.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of verification reports
    """
    try:
        # Query verification reports with pagination
        reports = db.query(VerificationReport)\
            .order_by(VerificationReport.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Join with features to get feature names
        reports_list = []
        for report in reports:
            feature = db.query(Feature).filter(Feature.id == report.feature_id).first()
            report_dict = report.to_dict()
            report_dict["feature_name"] = feature.name if feature else "Unknown Feature"
            reports_list.append(report_dict)

        logger.info(f"Retrieved {len(reports_list)} verification reports for user {current_user.id}")

        return {
            "reports": reports_list,
            "total": len(reports_list),
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error retrieving verification reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")