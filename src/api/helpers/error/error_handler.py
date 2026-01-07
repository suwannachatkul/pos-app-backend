import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from config.settings import settings
from shared.logging import logger


def get_exception_localized_message(
    exc: HTTPException | StarletteHTTPException, lang: str = "en"
) -> tuple[str, str]:
    """
    Extracts error code and translates message.

    Args:
        exc: The HTTPException instance
        lang: Language code (en or ja)

    Returns:
        tuple[str, str]: (error_code, localized_message)
    """
    # Get error code from exception or default to UNKNOWN_ERROR
    code = exc.ERROR_CODE if hasattr(exc, "ERROR_CODE") else "UNKNOWN_ERROR"

    # Handle Starlette authentication errors
    if code == "UNKNOWN_ERROR":
        if exc.status_code == HTTP_401_UNAUTHORIZED:
            code = "auth.CREDENTIALS_EXCEPTION"
        if exc.status_code == HTTP_403_FORBIDDEN:
            code = "auth.NOT_AUTHORIZED"

    # Get translated message from settings
    message = settings.error_message_dict[lang].get(
        code, settings.error_message_dict[lang].get("DEFAULT", str(exc))
    )

    # Perform variable substitution
    variables = exc.VARS if hasattr(exc, "VARS") else {}
    for key, value in variables.items():
        message = message.replace(f"{{{{{key}}}}}", str(value))

    return code, message


def get_exception_status_code(exc: HTTPException | StarletteHTTPException) -> int:
    """
    Extracts HTTP status code from exception.
    Falls back to Starlette status codes for auth errors.

    Args:
        exc: The HTTPException instance

    Returns:
        int: HTTP status code
    """
    status_code = exc.STATUS_CODE if hasattr(exc, "STATUS_CODE") else 500

    # Override for Starlette auth exceptions
    if exc.status_code == HTTP_401_UNAUTHORIZED:
        status_code = 401
    if exc.status_code == HTTP_403_FORBIDDEN:
        status_code = 403

    return status_code


def error_handler(
    request: Request, exc: HTTPException | StarletteHTTPException
) -> JSONResponse:
    """
    Global error handler for HTTP exceptions with localization support.

    Args:
        request: FastAPI Request object
        exc: HTTPException instance

    Returns:
        JSONResponse: Formatted error response
    """
    # Log the exception with full traceback
    logger.error(f"Exception occurred: {exc}")
    logger.error(traceback.format_exc())

    # Detect language from Accept-Language header
    language = request.headers.get("Accept-Language", "en").lower()
    if "en" in language:
        language = "en"
    else:
        language = "ja"

    # Get localized message
    code, message = get_exception_localized_message(exc, language)

    # Get status code
    status_code = get_exception_status_code(exc)

    # Build error response
    error_body = {
        "code": code,
        "message": message,
    }

    # Return JSON response with headers
    response = JSONResponse(
        error_body,
        status_code=status_code,
        headers=exc.HEADERS if hasattr(exc, "HEADERS") else {},
    )
    return response


async def http_exception_handler(
    request: Request, exc: HTTPException | StarletteHTTPException | Exception
) -> Response:
    """Async wrapper for HTTP exception handler."""
    return error_handler(request, exc)  # type: ignore[arg-type]


async def general_exception_handler(request: Request, exc: Exception) -> Response:
    """
    Global exception handler for unexpected errors.

    Args:
        request: FastAPI Request object
        exc: Exception instance

    Returns:
        JSONResponse: Formatted error response
    """
    # Log the unexpected exception
    logger.error(f"Unexpected exception occurred: {exc}")
    logger.error(traceback.format_exc())

    # Detect language from Accept-Language header
    language = request.headers.get("Accept-Language", "en").lower()
    if "en" in language:
        language = "en"
    else:
        language = "ja"

    # Get default error message
    message = settings.error_message_dict[language].get(
        "DEFAULT", "Internal server error"
    )

    return JSONResponse(
        status_code=500,
        content={
            "code": "UNKNOWN_ERROR",
            "message": message,
        },
    )
