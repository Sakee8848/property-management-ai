# 导入所有模型以确保它们被注册
from app.models.user import User, UserRole
from app.models.property import Property, PropertyUnit
from app.models.document import Document, DocumentCategory
from app.models.payment import Bill, Payment, FeeType, PaymentStatus, PaymentMethod
from app.models.message import Conversation, Message, MessageRole, ConversationStatus

__all__ = [
    "User",
    "UserRole",
    "Property",
    "PropertyUnit",
    "Document",
    "DocumentCategory",
    "Bill",
    "Payment",
    "FeeType",
    "PaymentStatus",
    "PaymentMethod",
    "Conversation",
    "Message",
    "MessageRole",
    "ConversationStatus",
]
