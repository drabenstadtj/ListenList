import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_path="db/listenlist.db"):
        self.connection = None
        self.db_path = db_path
        self.initialize_db()

    def initialize_db(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create the submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    album_id TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create the ratings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    album_id TEXT NOT NULL,
                    rating INTEGER,
                    comment TEXT,
                    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            print("Database initialized with submissions and ratings tables")
        except Error as e:
            print(f"Error initializing database: {e}")

    def add_submission(self, user_id, album_id):
        """Add a new album submission to the submissions table."""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO submissions (user_id, album_id)
            VALUES (?, ?)
        ''', (user_id, album_id))
        self.connection.commit()
        return cursor.lastrowid

    def remove_submission(self, user_id, album_id):
        """Remove a submission from the submissions table."""
        cursor = self.connection.cursor()
        cursor.execute('''
            DELETE FROM submissions WHERE user_id = ? AND album_id = ?
        ''', (user_id, album_id))
        self.connection.commit()
        return cursor.rowcount > 0  # Returns True if a row was deleted, False otherwise

    def submission_exists(self, user_id, album_id):
        """Check if an album has already been submitted by a user."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM submissions WHERE user_id = ? AND album_id = ?
        ''', (user_id, album_id))
        return cursor.fetchone() is not None

    # Rating Helpers
    def add_rating(self, user_id, album_id, rating, comment=None):
        """Add a new rating to the ratings table."""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO ratings (user_id, album_id, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, album_id, rating, comment))
        self.connection.commit()
        return cursor.lastrowid
    
    def update_rating(self, user_id, album_id, rating, comment=None):
        """Update an existing rating in the ratings table."""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE ratings
            SET rating = ?, comment = ?, rated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND album_id = ?
        ''', (rating, comment, user_id, album_id))
        self.connection.commit()
        return cursor.rowcount > 0  # Returns True if a row was updated, False otherwise


    def get_ratings_for_album(self, album_id):
        """Retrieve all ratings for a specific album."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT user_id, rating, comment FROM ratings WHERE album_id = ?
        ''', (album_id,))
        return cursor.fetchall()

    def get_user_rating_for_album(self, user_id, album_id):
        """Retrieve a specific user's rating for an album if it exists."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT rating, comment FROM ratings WHERE user_id = ? AND album_id = ?
        ''', (user_id, album_id))
        return cursor.fetchone()
    
    def get_user_submissions(self, user_id):
        """Retrieve all submissions made by a specific user."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT album_id, submitted_at 
            FROM submissions 
            WHERE user_id = ?
        ''', (user_id,))
        
        # Fetch all results and return them as a list of dictionaries
        submissions = cursor.fetchall()
        return [{"album_id": row[0], "submitted_at": row[1]} for row in submissions]

    def close_connection(self):
        if self.connection:
            self.connection.close()
