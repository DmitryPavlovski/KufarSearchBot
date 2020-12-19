import psycopg2
import config

class PostgresqlHandler:
    """Class for work with postgresql database"""
    def __init__(self):
        self.connection = psycopg2.connect(
            host=config.HOST,
            database=config.DATABASE,
            user="StreepBot",
            password="StreepBot")
        self.cursor = self.connection.cursor()

    def get_subscribers(self, status=True):
        """Method for get subscriders with need status"""
        status = str(status)
        with self.connection:
            self.cursor.execute("SELECT * FROM \"Subcribers\" WHERE \"is_active\" = %s", [status])
            return self.cursor.fetchall()
    
    def subscriber_exists(self, user_id):
        """Check on subscribe"""
        with self.connection:
            self.cursor.execute("SELECT * FROM \"Subcribers\" WHERE \"user_id\" = %s", [user_id])
            return bool(len(self.cursor.fetchall()))

    def add_subscriber(self, user_id, status = True):
        """Add subscriber"""
        with self.connection:
            return self.cursor.execute("INSERT INTO \"Subcribers\" (\"user_id\", \"is_active\") VALUES(%s,%s)", [user_id, status])

    def update_subscription(self, user_id, status):
        """Update active status"""
        with self.connection:
            return self.cursor.execute("UPDATE \"Subcribers\" SET \"is_active\" = %s WHERE \"user_id\" = %s", [status, user_id])

    def close(self):
        """Close connection"""
        self.connection.close()
