from app.shared.enums import MembershipRole, UserRole

# Permission -> roles that hold it
PERMISSIONS: dict[str, set[UserRole]] = {
    # User management
    "user:read_self": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "user:update_self": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "user:read_all": {UserRole.PLATFORM_ADMIN},
    "user:delete": {UserRole.PLATFORM_ADMIN},
    # Organization
    "org:read": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "org:update": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "org:delete": {UserRole.PLATFORM_ADMIN},
    "org:manage_members": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    # Courses
    "course:read": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "course:create": {UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "course:update": {UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "course:delete": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    # Exercises
    "exercise:read": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "exercise:create": {UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "exercise:submit": {UserRole.STUDENT},
    # Projects
    "project:read": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "project:create": {UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "project:submit": {UserRole.STUDENT},
    "project:evaluate": {UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    # AI
    "ai:tutor": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "ai:code_review": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "ai:debug": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    # Analytics
    "analytics:read_self": {UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "analytics:read_org": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
    "analytics:read_all": {UserRole.PLATFORM_ADMIN},
    # Admin
    "admin:access": {UserRole.PLATFORM_ADMIN},
    "admin:audit_logs": {UserRole.PLATFORM_ADMIN},
    # Billing
    "billing:manage": {UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN},
}


def has_permission(role: UserRole, permission: str) -> bool:
    allowed = PERMISSIONS.get(permission, set())
    return role in allowed


def role_to_membership(role: UserRole) -> MembershipRole:
    mapping = {
        UserRole.STUDENT: MembershipRole.STUDENT,
        UserRole.INSTRUCTOR: MembershipRole.INSTRUCTOR,
        UserRole.ORG_ADMIN: MembershipRole.ADMIN,
        UserRole.PLATFORM_ADMIN: MembershipRole.ADMIN,
    }
    return mapping.get(role, MembershipRole.STUDENT)
