# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Exceptions           ║
# ╚══════════════════════════════════════════╝


class MissCherryException(Exception):
    """Base exception for Miss Cherry Bot"""
    pass

class NotAdminError(MissCherryException):
    """User is not an admin"""
    pass

class NotSudoError(MissCherryException):
    """User is not a sudo user"""
    pass

class NotOwnerError(MissCherryException):
    """User is not the owner"""
    pass

class UserNotFoundError(MissCherryException):
    """Target user not found"""
    pass

class InvalidTimeError(MissCherryException):
    """Invalid time format provided"""
    pass
