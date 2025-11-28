"""
Supabase client для дополнительных функций.
"""

from supabase import create_client, Client
from .config import settings

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)

class SupabaseService:
    """Service for Supabase-specific operations."""

    @staticmethod
    async def insert_user_data(telegram_id: int, data: dict):
        """Insert user data into Supabase."""
        try:
            response = supabase.table('users').insert({
                'telegram_id': telegram_id,
                **data
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error inserting user data: {e}")
            return None

    @staticmethod
    async def get_user_stats():
        """Get user statistics."""
        try:
            users_count = supabase.table('users').select('id', count='exact').execute()
            orders_count = supabase.table('orders').select('id', count='exact').execute()
            active_users = supabase.table('users').select('id', count='exact').eq('subscribed', True).execute()

            return {
                'total_users': users_count.count,
                'total_orders': orders_count.count,
                'active_users': active_users.count
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None

    @staticmethod
    async def sync_gallery_items(items: dict):
        """Sync gallery items with Supabase."""
        try:
            # Clear existing items
            supabase.table('gallery_items').delete().neq('id', '0').execute()

            # Insert new items
            for item_id, item_data in items.items():
                supabase.table('gallery_items').insert({
                    'id': item_id,
                    **item_data
                }).execute()

            return True
        except Exception as e:
            print(f"Error syncing gallery: {e}")
            return False
