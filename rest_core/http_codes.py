# ====================================================================
# http_codes.py
# ====================================================================

from __future__ import annotations

from enum import IntEnum


# ====================================================================
# HTTP_Codes
# ====================================================================
class HTTP_Codes(IntEnum):
    """
    HTTP status codes с пояснительной фразой (httpx)
    """

    def __new__(
        cls,
        value: int,
        phrase: str = ""
    ) -> HTTP_Codes:
    
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase  # type: ignore[attr-defined]
        return obj

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def get_reason_phrase(cls, value: int) -> str:
        try:
            return cls(value).phrase  # type: ignore
        except ValueError:
            return ""

    @classmethod
    def is_informational(cls, value: int) -> bool:
        """
        status codes 1xx
        """
        return 100 <= value <= 199

    @classmethod
    def is_success(cls, value: int) -> bool:
        """
        status codes 2xx
        """
        return 200 <= value <= 299

    @classmethod
    def is_redirect(cls, value: int) -> bool:
        """
        status codes 3xx
        """
        return 300 <= value <= 399

    @classmethod
    def is_client_error(cls, value: int) -> bool:
        """
        status codes 4xx
        """
        return 400 <= value <= 499

    @classmethod
    def is_server_error(cls, value: int) -> bool:
        """
        status codes 5xx
        """
        return 500 <= value <= 599

    @classmethod
    def is_error(cls, value: int) -> bool:
        """
        status codes 4xx or 5xx
        """
        return 400 <= value <= 599

    # informational
    CONTINUE = 100, "Continue"
    SWITCHING_PROTOCOLS = 101, "Switching Protocols"
    PROCESSING = 102, "Processing"
    EARLY_HINTS = 103, "Early Hints"

    # success
    OK = 200, "OK"
    CREATED = 201, "Created"
    ACCEPTED = 202, "Accepted"
    NON_AUTHORITATIVE_INFORMATION = 203, "Non-Authoritative Information"
    NO_CONTENT = 204, "No Content"
    RESET_CONTENT = 205, "Reset Content"
    PARTIAL_CONTENT = 206, "Partial Content"
    MULTI_STATUS = 207, "Multi-Status"
    ALREADY_REPORTED = 208, "Already Reported"
    IM_USED = 226, "IM Used"

    # redirection
    MULTIPLE_CHOICES = 300, "Multiple Choices"
    MOVED_PERMANENTLY = 301, "Moved Permanently"
    FOUND = 302, "Found"
    SEE_OTHER = 303, "See Other"
    NOT_MODIFIED = 304, "Not Modified"
    USE_PROXY = 305, "Use Proxy"
    TEMPORARY_REDIRECT = 307, "Temporary Redirect"
    PERMANENT_REDIRECT = 308, "Permanent Redirect"

    # client error
    BAD_REQUEST = 400, "Bad Request"
    UNAUTHORIZED = 401, "Unauthorized"
    PAYMENT_REQUIRED = 402, "Payment Required"
    FORBIDDEN = 403, "Forbidden"
    NOT_FOUND = 404, "Not Found"
    METHOD_NOT_ALLOWED = 405, "Method Not Allowed"
    NOT_ACCEPTABLE = 406, "Not Acceptable"
    PROXY_AUTHENTICATION_REQUIRED = 407, "Proxy Authentication Required"
    REQUEST_TIMEOUT = 408, "Request Timeout"
    CONFLICT = 409, "Conflict"
    GONE = 410, "Gone"
    LENGTH_REQUIRED = 411, "Length Required"
    PRECONDITION_FAILED = 412, "Precondition Failed"
    REQUEST_ENTITY_TOO_LARGE = 413, "Request Entity Too Large"
    REQUEST_URI_TOO_LONG = 414, "Request-URI Too Long"
    UNSUPPORTED_MEDIA_TYPE = 415, "Unsupported Media Type"
    REQUESTED_RANGE_NOT_SATISFIABLE = 416, "Requested Range Not Satisfiable"
    EXPECTATION_FAILED = 417, "Expectation Failed"
    IM_A_TEAPOT = 418, "I'm a teapot"
    MISDIRECTED_REQUEST = 421, "Misdirected Request"
    UNPROCESSABLE_ENTITY = 422, "Unprocessable Entity"
    LOCKED = 423, "Locked"
    FAILED_DEPENDENCY = 424, "Failed Dependency"
    TOO_EARLY = 425, "Too Early"
    UPGRADE_REQUIRED = 426, "Upgrade Required"
    PRECONDITION_REQUIRED = 428, "Precondition Required"
    TOO_MANY_REQUESTS = 429, "Too Many Requests"
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431, "Request Header Fields Too Large"
    UNAVAILABLE_FOR_LEGAL_REASONS = 451, "Unavailable For Legal Reasons"

    # server errors
    INTERNAL_SERVER_ERROR = 500, "Internal Server Error"
    NOT_IMPLEMENTED = 501, "Not Implemented"
    BAD_GATEWAY = 502, "Bad Gateway"
    SERVICE_UNAVAILABLE = 503, "Service Unavailable"
    GATEWAY_TIMEOUT = 504, "Gateway Timeout"
    HTTP_VERSION_NOT_SUPPORTED = 505, "HTTP Version Not Supported"
    VARIANT_ALSO_NEGOTIATES = 506, "Variant Also Negotiates"
    INSUFFICIENT_STORAGE = 507, "Insufficient Storage"
    LOOP_DETECTED = 508, "Loop Detected"
    NOT_EXTENDED = 510, "Not Extended"
    NETWORK_AUTHENTICATION_REQUIRED = 511, "Network Authentication Required"


# pprint(HTTP_Codes.__dict__)

# Include lower-case styles for compatibility.
for code in HTTP_Codes:
    setattr(HTTP_Codes, code._name_.lower(), int(code))


## Test...
##----------------------------------
# from pprint import pprint
# if __name__ == '__main__':
#     print('='*80)    
#     pprint(HTTP_Codes.__dict__)
#     print(HTTP_Codes.ok)
#     print(HTTP_Codes.OK)
#     print(HTTP_Codes.is_success(201))
#     print(HTTP_Codes(204) == HTTP_Codes.NO_CONTENT)
#     x = HTTP_Codes(204)
#     q = x.phrase
#     y = HTTP_Codes.NO_CONTENT
#     print(HTTP_Codes.NO_CONTENT)
