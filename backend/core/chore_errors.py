"""
Chore-Specific Error Codes and Exceptions

Provides detailed error handling for chore operations with user-friendly messages
optimized for wall-mounted family dashboard display.
"""

from enum import Enum
from typing import Any, Dict, Optional

from .exceptions import DashboardException


class ChoreErrorCode(str, Enum):
    """Specific error codes for chore operations."""

    # Chore completion errors
    WEEKLY_POINT_CAP_EXCEEDED = "WEEKLY_POINT_CAP_EXCEEDED"
    CHORE_FREQUENCY_RESTRICTION = "CHORE_FREQUENCY_RESTRICTION"
    CHORE_NOT_AVAILABLE = "CHORE_NOT_AVAILABLE"
    CHORE_ALREADY_COMPLETED = "CHORE_ALREADY_COMPLETED"
    CHORE_DISABLED = "CHORE_DISABLED"

    # Parent confirmation errors
    PENDING_COMPLETION_NOT_FOUND = "PENDING_COMPLETION_NOT_FOUND"
    COMPLETION_ALREADY_CONFIRMED = "COMPLETION_ALREADY_CONFIRMED"
    PARENT_ACCESS_DENIED = "PARENT_ACCESS_DENIED"

    # Member/household errors
    MEMBER_NOT_FOUND = "MEMBER_NOT_FOUND"
    MEMBER_INACTIVE = "MEMBER_INACTIVE"
    INVALID_MEMBER_FOR_CHORE = "INVALID_MEMBER_FOR_CHORE"

    # Room/chore structure errors
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    CHORE_NOT_FOUND = "CHORE_NOT_FOUND"
    INVALID_ROOM_ACCESS = "INVALID_ROOM_ACCESS"


class ChoreValidationException(DashboardException):
    """Raised when chore validation fails with specific error codes."""

    def __init__(
        self,
        error_code: ChoreErrorCode,
        message: str,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code.value,
            details=details
        )
        self.user_message = user_message or message
        self.chore_error_code = error_code


# Pre-defined error messages optimized for wall dashboard display
CHORE_ERROR_MESSAGES = {
    ChoreErrorCode.WEEKLY_POINT_CAP_EXCEEDED: {
        "message": "Weekly point cap reached (30 points)",
        "user_message": "🎯 Weekly Goal Reached!\nYou've earned your maximum 30 points this week. Great job!",
        "action": "Try again next week or ask a parent to confirm pending tasks."
    },

    ChoreErrorCode.CHORE_FREQUENCY_RESTRICTION: {
        "message": "Chore is not available yet due to frequency restrictions",
        "user_message": "⏰ Chore Not Ready Yet\nThis chore can't be done again until tomorrow.",
        "action": "Check back later or choose a different chore."
    },

    ChoreErrorCode.CHORE_NOT_AVAILABLE: {
        "message": "Chore is currently not available",
        "user_message": "❌ Chore Unavailable\nThis chore isn't available right now.",
        "action": "Choose a different chore or ask a parent for help."
    },

    ChoreErrorCode.CHORE_ALREADY_COMPLETED: {
        "message": "Chore has already been completed",
        "user_message": "✅ Already Done!\nSomeone already completed this chore.",
        "action": "Choose a different chore to earn points."
    },

    ChoreErrorCode.CHORE_DISABLED: {
        "message": "Chore has been disabled by parent",
        "user_message": "🚫 Chore Disabled\nThis chore has been turned off by a parent.",
        "action": "Choose a different chore or ask a parent."
    },

    ChoreErrorCode.PENDING_COMPLETION_NOT_FOUND: {
        "message": "Pending completion not found",
        "user_message": "🔍 Task Not Found\nCouldn't find the task to confirm.",
        "action": "The task may have already been handled."
    },

    ChoreErrorCode.COMPLETION_ALREADY_CONFIRMED: {
        "message": "Completion has already been confirmed or rejected",
        "user_message": "✅ Already Confirmed\nThis task has already been reviewed.",
        "action": "No further action needed."
    },

    ChoreErrorCode.PARENT_ACCESS_DENIED: {
        "message": "Parent access required for this action",
        "user_message": "🔒 Parent Access Required\nOnly parents can perform this action.",
        "action": "Ask a parent to complete this task."
    },

    ChoreErrorCode.MEMBER_NOT_FOUND: {
        "message": "Household member not found",
        "user_message": "👤 Member Not Found\nCouldn't find the family member.",
        "action": "Check the member selection or ask a parent."
    },

    ChoreErrorCode.MEMBER_INACTIVE: {
        "message": "Household member is inactive",
        "user_message": "😴 Member Inactive\nThis family member's account is not active.",
        "action": "Ask a parent to activate the account."
    },

    ChoreErrorCode.CHORE_NOT_FOUND: {
        "message": "Chore not found",
        "user_message": "🔍 Chore Not Found\nCouldn't find this chore.",
        "action": "The chore may have been removed. Try refreshing."
    },

    ChoreErrorCode.ROOM_NOT_FOUND: {
        "message": "Room not found",
        "user_message": "🏠 Room Not Found\nCouldn't find this room.",
        "action": "The room may have been removed. Try refreshing."
    }
}


def create_chore_error(
    error_code: ChoreErrorCode,
    custom_message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> ChoreValidationException:
    """
    Create a standardized chore validation error with user-friendly messages.

    Args:
        error_code: The specific chore error code
        custom_message: Optional custom message (falls back to predefined)
        details: Additional error details

    Returns:
        ChoreValidationException: Configured exception with user-friendly messages
    """
    error_info = CHORE_ERROR_MESSAGES.get(error_code, {
        "message": "Chore operation failed",
        "user_message": "❌ Something Went Wrong\nPlease try again or ask a parent for help.",
        "action": "Try again later."
    })

    message = custom_message or error_info["message"]

    # Enhance details with user-friendly information
    enhanced_details = {
        "user_message": error_info["user_message"],
        "suggested_action": error_info["action"],
        "error_type": "chore_validation_error",
        **(details or {})
    }

    return ChoreValidationException(
        error_code=error_code,
        message=message,
        user_message=error_info["user_message"],
        details=enhanced_details
    )


def create_point_cap_error(current_points: int, max_points: int = 30) -> ChoreValidationException:
    """Create a specific error for weekly point cap with current progress."""
    details = {
        "current_points": current_points,
        "max_points": max_points,
        "points_remaining": 0,
        "user_message": f"🎯 Weekly Goal Reached!\nYou've earned {current_points}/{max_points} points this week. Great job!",
        "suggested_action": "Try again next week or ask a parent to confirm pending tasks."
    }

    return ChoreValidationException(
        error_code=ChoreErrorCode.WEEKLY_POINT_CAP_EXCEEDED,
        message=f"Weekly point cap reached ({current_points}/{max_points} points)",
        details=details
    )


def create_frequency_restriction_error(
    chore_name: str,
    next_available: str
) -> ChoreValidationException:
    """Create a specific error for chore frequency restrictions."""
    details = {
        "chore_name": chore_name,
        "next_available": next_available,
        "user_message": f"⏰ '{chore_name}' Not Ready Yet\nThis chore will be available {next_available}.",
        "suggested_action": "Check back later or choose a different chore."
    }

    return ChoreValidationException(
        error_code=ChoreErrorCode.CHORE_FREQUENCY_RESTRICTION,
        message=f"Chore '{chore_name}' is not available until {next_available}",
        details=details
    )