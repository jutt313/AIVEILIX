"""
Shared dependencies for FastAPI routers.
"""
from fastapi import Depends
from typing import Optional
from app.routers.buckets import get_current_user_id
from app.services.team_service import get_team_member_context


class UserContext:
    """Holds the authenticated user's identity and team info."""

    def __init__(
        self,
        user_id: str,
        is_team_member: bool = False,
        owner_id: Optional[str] = None,
        team_member_id: Optional[str] = None,
        color: Optional[str] = None,
        name: Optional[str] = None,
        show_name: Optional[bool] = None,
    ):
        self.user_id = user_id
        self.is_team_member = is_team_member
        self.owner_id = owner_id or user_id
        self.team_member_id = team_member_id
        self.color = color
        self.name = name
        self.show_name = show_name

    @property
    def effective_user_id(self) -> str:
        """The owner_id for team members, user_id for owners."""
        return self.owner_id


async def get_user_context(user_id: str = Depends(get_current_user_id)) -> UserContext:
    """Dependency that wraps get_current_user_id + team context lookup."""
    ctx = get_team_member_context(user_id)
    if ctx:
        return UserContext(
            user_id=user_id,
            is_team_member=True,
            owner_id=ctx["owner_id"],
            team_member_id=ctx["team_member_id"],
            color=ctx["color"],
            name=ctx["name"],
            show_name=ctx["show_name"],
        )
    return UserContext(user_id=user_id)
