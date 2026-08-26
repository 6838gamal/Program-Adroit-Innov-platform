# /app/app/modules/ai/agents/__init__.py

from .agents import CodeReviewAgent, OtherAgent

# أو إذا أردت تصدير كل الكلاسات
__all__ = ['CodeReviewAgent', 'OtherAgent']
