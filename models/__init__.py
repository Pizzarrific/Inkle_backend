# models/__init__.py
from .users import init_users_table
from .posts import init_posts_table
from .likes import init_likes_table
from .comments import init_comments_table
from .followers import init_followers_table
from .blocks import init_blocks_table
from .activity import init_activity_table
from .notifications import init_notifications_table

def init_all_tables():
    init_users_table()
    init_posts_table()
    init_likes_table()
    init_comments_table()
    init_followers_table()
    init_blocks_table()
    init_activity_table()
    init_notifications_table()
