"""Domain errors raised by the service layer and mapped to HTTP codes in main.py.

Keeping HTTP out of the service layer means the same logic could be reused by a
worker, a CLI, or a future split-out service.
"""


class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409


class Unauthorized(DomainError):
    status_code = 401


class Forbidden(DomainError):
    status_code = 403
