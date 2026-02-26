class ProjectNotFound(Exception):
    pass


class PermissionDenied(Exception):
    pass


class ConflictError(Exception):
    pass


class InvalidStateTransition(Exception):
    pass