from app.core.db import get_db
from app.core.security import require_role

require_editor = require_role(["editor", "admin"])
require_admin = require_role(["admin"])
