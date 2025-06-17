from sqlalchemy.orm import relationship
from .user import User
from .organization import Organization
from .user_preferences import UserPreferences

# Now that all models are loaded, patch the relationships
User.organization = relationship("Organization", back_populates="users")
User.preferences = relationship("UserPreferences", back_populates="user")
#User.chats = relationship("UserPreferences", back_populates="user")

__all__ = ["User", "Organization", "UserPreferences"]

