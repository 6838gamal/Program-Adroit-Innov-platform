import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ORG_ADMIN = "org_admin"
    PLATFORM_ADMIN = "platform_admin"


class MembershipRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PAUSED = "paused"


class ExerciseType(str, enum.Enum):
    CODE = "code"
    MULTIPLE_CHOICE = "multiple_choice"
    DEBUGGING = "debugging"
    OUTPUT_PREDICTION = "output_prediction"
    SHORT_ANSWER = "short_answer"


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class ProjectStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class ProficiencyLevel(str, enum.Enum):
    NONE = "none"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningEventType(str, enum.Enum):
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    EXERCISE_STARTED = "exercise_started"
    EXERCISE_SUBMITTED = "exercise_submitted"
    EXERCISE_PASSED = "exercise_passed"
    EXERCISE_FAILED = "exercise_failed"
    HINT_REQUESTED = "hint_requested"
    AI_HELP_REQUESTED = "ai_help_requested"
    PROJECT_STARTED = "project_started"
    PROJECT_COMPLETED = "project_completed"


class NotificationType(str, enum.Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class BillingPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"
