#!/usr/bin/env python3
import os
import requests
import gzip
import shutil
import mysql.connector
import logging
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://rebrickable.com/downloads/"
TEMP_DIR = "temp"
SQL_OUTPUT_DIR = "sql_output"
LOG_DIR = "logs"
REQUIRED_FILES = {
    'sets.csv.gz': 'sets',
    'inventory_sets.csv.gz': 'inventory_sets',
    'inventory_minifigs.csv.gz': 'inventory_minifigs',
    'minifigs.csv.gz': 'minifigs',
    'themes.csv.gz': 'themes',
    'inventories.csv.gz': 'inventories'
}

def setup_directories():
    """Create necessary directories if they don't exist."""
    for directory in [TEMP_DIR, SQL_OUTPUT_DIR, LOG_DIR]:
        os.makedirs(directory, exist_ok=True)

def download_and_extract_files():
    """Download required .gz files and extract them."""
    # Create session with headers to avoid blocking
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    logger.info("Fetching download page...")
    response = session.get(BASE_URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a'):
        filename = link.text.strip()
        if filename in REQUIRED_FILES:
            file_url = link.get('href')
            if not file_url.startswith('http'):
                file_url = f"https://rebrickable.com{file_url}"
            
            gz_path = os.path.join(TEMP_DIR, filename)
            logger.info(f"Downloading {filename}")
            
            # Add delay between downloads to avoid rate limiting
            time.sleep(random.uniform(2, 5))
            
            try:
                response = session.get(file_url, timeout=60)
                response.raise_for_status()
                
                with open(gz_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Successfully downloaded {filename} ({len(response.content)} bytes)")
                
                # Extract the gzip file
                csv_path = os.path.join(TEMP_DIR, filename[:-3])
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(csv_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                os.remove(gz_path)
                logger.info(f"Extracted and cleaned up {filename}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {filename}: {e}")
                continue

def execute_sql_files(host, user, password, database, port='3306'):
    """Execute all generated SQL files against the database."""
    try:
        conn = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password, 
            database=database,
            port=int(port)
        )
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS popular_themes (
                id int NOT NULL AUTO_INCREMENT,
                theme_id int NOT NULL,
                collection_count int NOT NULL,
                snapshot_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY theme_id (theme_id),
                KEY snapshot_date (snapshot_date),
                CONSTRAINT popular_themes_ibfk_1 FOREIGN KEY (theme_id) REFERENCES themes (id)
            )
        """)
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recent_set_additions (
                id int NOT NULL AUTO_INCREMENT,
                set_num varchar(20) DEFAULT NULL,
                theme_id int DEFAULT NULL,
                added_date timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY set_num (set_num),
                KEY theme_id (theme_id),
                CONSTRAINT recent_set_additions_ibfk_1 FOREIGN KEY (set_num) REFERENCES sets (set_num),
                CONSTRAINT recent_set_additions_ibfk_2 FOREIGN KEY (theme_id) REFERENCES themes (id)
            )
        """)
        conn.commit()
        
        # Execute files in order
        order = ['themes', 'sets', 'minifigs', 'inventories', 'inventory_minifigs', 'inventory_sets']
        
        for table in order:
            file = f"{table}_inserts.sql"
            if file in os.listdir(SQL_OUTPUT_DIR):
                file_path = os.path.join(SQL_OUTPUT_DIR, file)
                logger.info(f"Executing SQL file: {file}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_commands = f.read().split(';')
                    
                    for command in sql_commands:
                        if command.strip():
                            try:
                                cursor.execute(command)
                                conn.commit()
                            except mysql.connector.Error as err:
                                logger.error(f"Error executing SQL: {err}")
                                continue
        
        # Update popular themes
        logger.info("Updating popular themes statistics")
        try:
            cursor.execute("DELETE FROM popular_themes")
            conn.commit()

            cursor.execute("""
                INSERT INTO popular_themes (theme_id, collection_count)
                SELECT 
                    COALESCE(parent.id, t.id) as theme_id,
                    COUNT(DISTINCT c.id) as collection_count
                FROM sets s
                JOIN themes t ON t.id = s.theme_id
                LEFT JOIN themes parent ON t.parent_id = parent.id
                JOIN collection c ON c.set_num = s.set_num
                GROUP BY COALESCE(parent.id, t.id)
                ORDER BY collection_count DESC
                LIMIT 5
            """)
            conn.commit()

        except mysql.connector.Error as err:
            logger.error(f"Error updating popular themes: {err}")

        # Update recent set additions
        logger.info("Updating recent set additions")
        try:
            cursor.execute("DELETE FROM recent_set_additions")
            conn.commit()

            cursor.execute("""
                INSERT INTO recent_set_additions (set_num, theme_id)
                SELECT set_num, theme_id
                FROM (
                    SELECT 
                        s.set_num,
                        COALESCE(parent.id, t.id) as theme_id,
                        ROW_NUMBER() OVER (
                            PARTITION BY COALESCE(parent.id, t.id)
                            ORDER BY s.year DESC, s.set_num DESC
                        ) as rn
                    FROM sets s
                    JOIN themes t ON t.id = s.theme_id
                    LEFT JOIN themes parent ON t.parent_id = parent.id
                    JOIN popular_themes pt ON COALESCE(parent.id, t.id) = pt.theme_id
                    WHERE s.year IS NOT NULL
                ) ranked
                WHERE rn <= 5
            """)
            conn.commit()

        except mysql.connector.Error as err:
            logger.error(f"Error updating recent set additions: {err}")
            
        return cursor, conn
        
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def cleanup():
    """Clean up temporary files."""
    logger.info("Cleaning up temporary files")
    for file in os.listdir(TEMP_DIR):
        if file != '.gitkeep':
            os.remove(os.path.join(TEMP_DIR, file))

def main():
    try:
        logger.info("Starting LEGO data update process...")
        
        # Load environment variables
        load_dotenv('.env')
        
        db_host = os.getenv('SQL_DB_HOST')
        db_user = os.getenv('SQL_DB_USER')
        db_pass = os.getenv('SQL_DB_PASS')
        db_name = os.getenv('SQL_DB_NAME')
        db_port = os.getenv('SQL_DB_PORT', '3306')  # Default to 3306 if not specified
        
        logger.info(f"Database connection: {db_user}@{db_host}:{db_port}/{db_name}")
        
        if not all([db_host, db_user, db_pass, db_name]):
            raise ValueError("Missing required environment variables. Please check SQL_DB_HOST, SQL_DB_USER, SQL_DB_PASS, SQL_DB_NAME")
        
        logger.info("Setting up directories...")
        setup_directories()
        
        logger.info("Downloading and extracting files from Rebrickable...")
        download_and_extract_files()
        
        logger.info("Generating SQL insert statements...")
        os.system('python3 generate_sql_insert.py')
        
        logger.info("Executing SQL files and updating database...")
        cursor, conn = execute_sql_files(db_host, db_user, db_pass, db_name, db_port)
        conn.close()
        
        logger.info("Cleaning up temporary files...")
        cleanup()
        
        logger.info("✅ Data update completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in main process: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()