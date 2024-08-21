from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        Initializes the role-based access control with a list of allowed roles.

        This constructor sets up the allowed roles for accessing certain resources or endpoints.
        Users with roles that are not in the allowed list will be restricted from accessing the resource.

        :param allowed_roles: A list of roles that are permitted to access the resource.
        :type allowed_roles: list[Role]
        :doc-author: Trelent
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Middleware function that checks if the current user has one of the allowed roles.

        This method is called to verify if the user's role is among the allowed roles for accessing a particular resource.
        If the user's role is not in the list of allowed roles, an HTTP 403 Forbidden exception is raised.

        :param request: The incoming HTTP request.
        :type request: Request
        :param user: The currently authenticated user.
        :type user: User
        :raises HTTPException: If the user's role is not among the allowed roles.
        :doc-author: Trelent
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN",
                )
