from typing import Optional, List
from fastapi import Header, HTTPException, status, Query

def extract_role(
    x_user_role: Optional[str] = None,
    authorization: Optional[str] = None,
    role: Optional[str] = None
) -> str:
    # 1. Direct role header (e.g. X-User-Role: admin)
    if x_user_role:
        role_clean = x_user_role.strip().lower()
        if role_clean in ("admin", "editor"):
            return role_clean

    # 2. Query param role
    if role:
        role_clean = role.strip().lower()
        if role_clean in ("admin", "editor"):
            return role_clean

    # 3. Authorization Bearer header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip().lower()
        if "admin" in token:
            return "admin"
        if "editor" in token:
            return "editor"

    # Default fallback to editor if unauthenticated or demo
    return "editor"


def require_role(allowed_roles: List[str]):
    def dependency(
        x_user_role: Optional[str] = Header(None),
        authorization: Optional[str] = Header(None),
        role: Optional[str] = Query(None)
    ) -> str:
        user_role = extract_role(x_user_role, authorization, role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role in {allowed_roles}, but current user has role '{user_role}'."
            )
        return user_role
    return dependency
