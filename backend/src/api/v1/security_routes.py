"""
Security API endpoints for the verification system.
This module provides endpoints for security scanning and assessment.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta
import asyncio
import subprocess
import os
from typing import Dict, Any

from ...database.database import get_db
from ...models.security_assessment import SecurityAssessment, SecurityScanType, SecurityScanStatus
from ...models.user import User
from ...middleware.auth import get_current_user
from ...utils.logging import get_logger


router = APIRouter(prefix="/security", tags=["security"])
logger = get_logger(__name__)


@router.get("/scans", summary="Get Security Scan Results")
async def get_security_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve security scan results.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of security scan results
    """
    try:
        # Query all security assessments
        scans = db.query(SecurityAssessment)\
            .order_by(SecurityAssessment.created_at.desc())\
            .all()

        scans_list = []
        for scan in scans:
            scan_dict = scan.to_dict()

            # Calculate total vulnerabilities
            total_vulnerabilities = (
                scan.critical_vulnerabilities +
                scan.high_vulnerabilities +
                scan.medium_vulnerabilities +
                scan.low_vulnerabilities
            )
            scan_dict["total_vulnerabilities"] = total_vulnerabilities

            # Add severity summary
            scan_dict["severity_summary"] = {
                "critical": scan.critical_vulnerabilities,
                "high": scan.high_vulnerabilities,
                "medium": scan.medium_vulnerabilities,
                "low": scan.low_vulnerabilities,
                "total": total_vulnerabilities
            }

            scans_list.append(scan_dict)

        logger.info(f"Retrieved {len(scans_list)} security scans for user {current_user.id}")

        return {
            "scans": scans_list
        }

    except Exception as e:
        logger.error(f"Error retrieving security scans: {str(e)}")
        raise


@router.get("/scans/latest", summary="Get Latest Security Scan Results")
async def get_latest_security_scan(
    scan_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve the latest security scan results.

    Args:
        scan_type: Type of scan to retrieve (optional)
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Latest security scan result
    """
    try:
        query = db.query(SecurityAssessment)

        if scan_type:
            query = query.filter(SecurityAssessment.scan_type == scan_type)

        latest_scan = query.order_by(SecurityAssessment.created_at.desc()).first()

        if not latest_scan:
            return {
                "scan": None,
                "message": f"No {'latest ' + scan_type + ' ' if scan_type else ''}scan found"
            }

        scan_dict = latest_scan.to_dict()

        # Calculate total vulnerabilities
        total_vulnerabilities = (
            latest_scan.critical_vulnerabilities +
            latest_scan.high_vulnerabilities +
            latest_scan.medium_vulnerabilities +
            latest_scan.low_vulnerabilities
        )
        scan_dict["total_vulnerabilities"] = total_vulnerabilities

        # Add severity summary
        scan_dict["severity_summary"] = {
            "critical": latest_scan.critical_vulnerabilities,
            "high": latest_scan.high_vulnerabilities,
            "medium": latest_scan.medium_vulnerabilities,
            "low": latest_scan.low_vulnerabilities,
            "total": total_vulnerabilities
        }

        logger.info(f"Retrieved latest security scan for user {current_user.id}")

        return {
            "scan": scan_dict
        }

    except Exception as e:
        logger.error(f"Error retrieving latest security scan: {str(e)}")
        raise


@router.post("/scans/run", summary="Run Security Scan")
async def run_security_scan(
    scan_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Run a security scan.

    Args:
        scan_data: Scan configuration data
        background_tasks: FastAPI background tasks
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Scan initiation response
    """
    try:
        # Validate scan type
        scan_type = scan_data.get("scan_type", "dependency_vulnerability").lower()
        try:
            scan_type_enum = SecurityScanType(scan_type)
        except ValueError:
            valid_types = [st.value for st in SecurityScanType]
            raise ValueError(f"Invalid scan type: {scan_type}. Valid types: {valid_types}")

        # Create a new security assessment record
        scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        security_assessment = SecurityAssessment(
            scan_id=scan_id,
            scan_type=scan_type,
            status="in_progress",
            is_automated=True
        )

        db.add(security_assessment)
        db.commit()
        db.refresh(security_assessment)

        # Schedule the security scan as a background task
        background_tasks.add_task(
            perform_security_scan_task,
            security_assessment.id,
            scan_type,
            scan_data.get("targets", []),
            db
        )

        response = {
            "scan_id": scan_id,
            "assessment_id": str(security_assessment.id),
            "status": "in_progress",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=10)).isoformat()  # Estimate 10 minutes
        }

        logger.info(f"Started security scan {scan_id} by user {current_user.id}")

        return response

    except Exception as e:
        logger.error(f"Error initiating security scan: {str(e)}")
        raise


async def perform_security_scan_task(
    assessment_id: uuid.UUID,
    scan_type: str,
    targets: List[str],
    db_session: Session
):
    """
    Background task to perform the actual security scan.

    Args:
        assessment_id: ID of the security assessment
        scan_type: Type of security scan to perform
        targets: Targets to scan
        db_session: Database session for this task
    """
    try:
        # Get a new database session for this background task
        from ...database.database import SessionLocal
        db = SessionLocal()

        try:
            # Get the security assessment
            assessment = db.query(SecurityAssessment)\
                .filter(SecurityAssessment.id == assessment_id).first()

            if not assessment:
                logger.error(f"Security assessment {assessment_id} not found")
                return

            # Simulate different types of security scans
            if scan_type == "dependency_vulnerability":
                # Simulate dependency vulnerability scan
                await asyncio.sleep(3)  # Simulate scan time

                # For demo purposes, generate simulated results
                assessment.critical_vulnerabilities = 1
                assessment.high_vulnerabilities = 3
                assessment.medium_vulnerabilities = 5
                assessment.low_vulnerabilities = 8
                assessment.findings = "Found vulnerabilities in dependencies: package-a, package-b, package-c"
                assessment.recommendations = [
                    "Update package-a to version 2.1.0 or later",
                    "Apply security patches to package-b",
                    "Consider alternative for package-c due to critical vulnerability"
                ]

            elif scan_type == "static_analysis":
                # Simulate static analysis scan
                await asyncio.sleep(5)  # Simulate scan time

                assessment.critical_vulnerabilities = 0
                assessment.high_vulnerabilities = 2
                assessment.medium_vulnerabilities = 4
                assessment.low_vulnerabilities = 6
                assessment.findings = "Potential security issues found in code: SQL injection possibility, weak crypto, etc."
                assessment.recommendations = [
                    "Review database queries for potential SQL injection",
                    "Use stronger cryptographic algorithms",
                    "Implement proper input validation"
                ]

            elif scan_type == "container_security":
                # Simulate container security scan
                await asyncio.sleep(4)  # Simulate scan time

                assessment.critical_vulnerabilities = 2
                assessment.high_vulnerabilities = 1
                assessment.medium_vulnerabilities = 3
                assessment.low_vulnerabilities = 4
                assessment.findings = "Vulnerabilities found in container image layers"
                assessment.recommendations = [
                    "Update base image to latest patched version",
                    "Remove unnecessary packages from container",
                    "Scan for CVEs in installed packages"
                ]
            else:
                # Default case - simulate generic scan
                await asyncio.sleep(2)  # Simulate scan time

                assessment.critical_vulnerabilities = 0
                assessment.high_vulnerabilities = 0
                assessment.medium_vulnerabilities = 2
                assessment.low_vulnerabilities = 3
                assessment.findings = "Basic security scan completed"
                assessment.recommendations = ["No critical issues found", "Review security best practices"]

            # Update status and completion time
            assessment.status = "completed"
            assessment.completed_at = datetime.utcnow()

            db.commit()

            logger.info(f"Completed security scan {assessment.scan_id} (assessment: {assessment_id})")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in security scan background task: {str(e)}")

        # Try to update the assessment with failure status
        try:
            from ...database.database import SessionLocal
            db = SessionLocal()

            assessment = db.query(SecurityAssessment)\
                .filter(SecurityAssessment.id == assessment_id).first()

            if assessment:
                assessment.status = "failed"
                assessment.findings = f"Scan failed: {str(e)}"
                assessment.completed_at = datetime.utcnow()

                db.commit()

            db.close()
        except Exception:
            pass  # If we can't update the status, there's nothing more we can do


@router.get("/vulnerability-summary", summary="Get Vulnerability Summary")
async def get_vulnerability_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get a summary of all vulnerabilities across all security scans.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Vulnerability summary
    """
    try:
        # Query all security assessments to get vulnerability summary
        assessments = db.query(SecurityAssessment).all()

        total_critical = sum(ass.critical_vulnerabilities for ass in assessments)
        total_high = sum(ass.high_vulnerabilities for ass in assessments)
        total_medium = sum(ass.medium_vulnerabilities for ass in assessments)
        total_low = sum(ass.low_vulnerabilities for ass in assessments)
        total_vulnerabilities = total_critical + total_high + total_medium + total_low

        # Count by scan type
        by_type: Dict[str, Dict[str, int]] = {}
        for assessment in assessments:
            scan_type = assessment.scan_type
            if scan_type not in by_type:
                by_type[scan_type] = {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "total": 0
                }

            by_type[scan_type]["critical"] += assessment.critical_vulnerabilities
            by_type[scan_type]["high"] += assessment.high_vulnerabilities
            by_type[scan_type]["medium"] += assessment.medium_vulnerabilities
            by_type[scan_type]["low"] += assessment.low_vulnerabilities
            by_type[scan_type]["total"] += (
                assessment.critical_vulnerabilities +
                assessment.high_vulnerabilities +
                assessment.medium_vulnerabilities +
                assessment.low_vulnerabilities
            )

        # Get latest scan date
        latest_scan_date = None
        if assessments:
            latest_scan_date = max(ass.created_at for ass in assessments).isoformat()

        summary = {
            "summary": {
                "total_vulnerabilities": total_vulnerabilities,
                "critical_vulnerabilities": total_critical,
                "high_vulnerabilities": total_high,
                "medium_vulnerabilities": total_medium,
                "low_vulnerabilities": total_low,
                "total_assessments": len(assessments),
                "latest_scan_date": latest_scan_date
            },
            "by_scan_type": by_type,
            "risk_level": determine_risk_level(total_critical, total_high, total_medium, total_low)
        }

        logger.info(f"Retrieved vulnerability summary for user {current_user.id}")

        return summary

    except Exception as e:
        logger.error(f"Error retrieving vulnerability summary: {str(e)}")
        raise


def determine_risk_level(critical: int, high: int, medium: int, low: int) -> str:
    """
    Determine overall risk level based on vulnerability counts.

    Args:
        critical: Number of critical vulnerabilities
        high: Number of high vulnerabilities
        medium: Number of medium vulnerabilities
        low: Number of low vulnerabilities

    Returns:
        str: Risk level (critical, high, medium, low, none)
    """
    if critical > 0:
        return "critical"
    elif high > 0:
        return "high"
    elif medium > 0:
        return "medium"
    elif low > 0:
        return "low"
    else:
        return "none"


@router.get("/compliance", summary="Get Compliance Status")
async def get_compliance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get security compliance status.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Compliance status
    """
    try:
        # For now, return a basic compliance status
        # In a real implementation, this would check against compliance frameworks
        summary = await get_vulnerability_summary(db, current_user)

        compliance_status = {
            "overall_compliance": "non_compliant" if summary["summary"]["critical_vulnerabilities"] > 0 else "compliant",
            "compliance_framework": "OWASP Top 10, CWE/SANS Top 25",
            "last_assessment_date": summary["summary"]["latest_scan_date"],
            "vulnerability_summary": summary["summary"],
            "recommendations": [
                "Address all critical vulnerabilities immediately",
                "Implement regular security scanning",
                "Follow security best practices",
                "Keep dependencies updated"
            ] if summary["summary"]["critical_vulnerabilities"] > 0 else [
                "Maintain current security posture",
                "Continue regular scanning",
                "Monitor for new vulnerabilities"
            ]
        }

        logger.info(f"Retrieved compliance status for user {current_user.id}")

        return compliance_status

    except Exception as e:
        logger.error(f"Error retrieving compliance status: {str(e)}")
        raise