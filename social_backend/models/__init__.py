# models/__init__.py

from .users import init_users_table
from .posts import init_posts_table
from .likes import init_likes_table
from .comments import init_comments_table
from .follow import init_follow_table       # correct file + function
from .block import init_block_table         # correct file + function
from .activity import init_activity_table
from .notifications import init_notifications_table

def init_all_tables():
    """Initialize all DB tables — call this once at app startup."""
    init_users_table()
    init_posts_table()
    init_likes_table()
    init_comments_table()
    init_follow_table()       # correct
    init_block_table()        # correct
    init_activity_table()
    init_notifications_table()
