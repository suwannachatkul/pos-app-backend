from fastapi import HTTPException


# ==================== Base Exceptions ====================


class APIValidationError(HTTPException):
    """400 - API Validation Error"""

    ERROR_CODE = "api.GENERAL_VALIDATION_ERROR"
    STATUS_CODE = 400
    VARS = {}

    def __init__(self, message: str) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = {"msg": message}


class BadRequestException(HTTPException):
    """400 - Bad Request"""

    ERROR_CODE = "api.BAD_REQUEST"
    STATUS_CODE = 400
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class UnauthorizedException(HTTPException):
    """401 - Unauthorized"""

    ERROR_CODE = "api.UNAUTHORIZED"
    STATUS_CODE = 401
    HEADERS = {"WWW-Authenticate": "Bearer"}
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class ForbiddenException(HTTPException):
    """403 - Forbidden"""

    ERROR_CODE = "api.FORBIDDEN"
    STATUS_CODE = 403
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class NotFoundException(HTTPException):
    """404 - Not Found"""

    ERROR_CODE = "api.NOT_FOUND"
    STATUS_CODE = 404
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class ConflictException(HTTPException):
    """409 - Conflict"""

    ERROR_CODE = "api.CONFLICT"
    STATUS_CODE = 409
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


# ==================== Auth Exceptions ====================


class CredentialsException(HTTPException):
    """401 - Invalid Credentials"""

    ERROR_CODE = "auth.CREDENTIALS_EXCEPTION"
    STATUS_CODE = 401
    HEADERS = {"WWW-Authenticate": "Bearer"}
    VARS = {}

    def __init__(self) -> None:
        super().__init__(status_code=self.STATUS_CODE)


class NotAuthorizedException(HTTPException):
    """403 - Not Authorized"""

    ERROR_CODE = "auth.NOT_AUTHORIZED"
    STATUS_CODE = 403
    VARS = {}

    def __init__(self) -> None:
        super().__init__(status_code=self.STATUS_CODE)


class UserNameAlreadyExists(HTTPException):
    """409 - Username Already Exists"""

    ERROR_CODE = "auth.USER_NAME_ALREADY_EXISTS"
    STATUS_CODE = 409
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class InvalidTokenException(HTTPException):
    """401 - Invalid Token"""

    ERROR_CODE = "auth.INVALID_TOKEN"
    STATUS_CODE = 401
    HEADERS = {"WWW-Authenticate": "Bearer"}
    VARS = {}

    def __init__(self) -> None:
        super().__init__(status_code=self.STATUS_CODE)


# ==================== GraphQL Exceptions ====================


class GraphQLQueryError(HTTPException):
    """400 - GraphQL Query Error"""

    ERROR_CODE = "graphql.QUERY_ERROR"
    STATUS_CODE = 400
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs


class GraphQLMutationError(HTTPException):
    """400 - GraphQL Mutation Error"""

    ERROR_CODE = "graphql.MUTATION_ERROR"
    STATUS_CODE = 400
    VARS = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=self.STATUS_CODE)
        self.VARS = kwargs
