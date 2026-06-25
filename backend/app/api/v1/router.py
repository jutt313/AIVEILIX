from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    buckets,
    files,
    uploads,
    categories,
    search,
    conversations,
    notifications,
    billing,
    account_mcp_tokens,
    mcp_server,
    mcp_tokens,
    mcp_tools,
    team,
    admin,
    admin_demo,
    demo,
    enterprise,
    internal,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(buckets.router)
router.include_router(files.router)
router.include_router(uploads.router)
router.include_router(categories.router)
router.include_router(search.router)
router.include_router(conversations.router)
router.include_router(notifications.router)
router.include_router(billing.router)
router.include_router(mcp_server.router)
router.include_router(mcp_tokens.router)
router.include_router(mcp_tools.router)
router.include_router(account_mcp_tokens.router)
router.include_router(team.router)
router.include_router(admin.router)
router.include_router(admin_demo.router)
router.include_router(demo.router)
router.include_router(enterprise.router)
router.include_router(internal.router)
