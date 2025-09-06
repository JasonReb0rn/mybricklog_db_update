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

# Cloudflare bypass imports
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

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

def get_page_with_cloudscraper(url):
    """Attempt to get page using cloudscraper to bypass Cloudflare."""
    if not CLOUDSCRAPER_AVAILABLE:
        return None
    
    try:
        logger.info("Attempting to bypass Cloudflare using cloudscraper...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        response = scraper.get(url, timeout=30)
        response.raise_for_status()
        logger.info("Successfully bypassed Cloudflare with cloudscraper")
        return response, scraper
        
    except Exception as e:
        logger.warning(f"Cloudscraper failed: {e}")
        return None

def get_page_with_selenium(url):
    """Attempt to get page using selenium as fallback."""
    if not SELENIUM_AVAILABLE:
        return None
    
    try:
        logger.info("Attempting to bypass Cloudflare using Selenium...")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Try headless first, fallback to headed if needed
        chrome_options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get(url)
        
        # Wait for page to load and Cloudflare to complete
        wait = WebDriverWait(driver, 30)
        
        # Wait for either the page content or a sign that Cloudflare is processing
        try:
            # Wait for content to appear (look for download links)
            wait.until(
                lambda driver: len(driver.find_elements(By.TAG_NAME, "a")) > 10 or
                              "gzip" in driver.page_source.lower()
            )
        except:
            # If that fails, just wait a bit for Cloudflare
            time.sleep(10)
        
        page_source = driver.page_source
        cookies = driver.get_cookies()
        
        driver.quit()
        
        logger.info("Successfully bypassed Cloudflare with Selenium")
        return page_source, cookies
        
    except Exception as e:
        logger.warning(f"Selenium failed: {e}")
        try:
            driver.quit()
        except:
            pass
        return None

def download_and_extract_files():
    """Download required .gz files and extract them."""
    session = None
    page_content = None
    cookies = None
    
    # Try different methods to bypass Cloudflare
    logger.info("Fetching download page...")
    
    # Method 1: Try cloudscraper first
    result = get_page_with_cloudscraper(BASE_URL)
    if result:
        response, session = result
        page_content = response.text
        logger.info("Using cloudscraper session for downloads")
    
    # Method 2: Try selenium if cloudscraper failed
    if not page_content:
        result = get_page_with_selenium(BASE_URL)
        if result:
            page_content, cookies = result
            logger.info("Using selenium-obtained page content")
            # Create a regular session with selenium cookies
            session = requests.Session()
            if cookies:
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
            
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': BASE_URL,
            })
    
    # Method 3: Fallback to regular requests (will likely fail with 403)
    if not page_content:
        logger.warning("All bypass methods failed, trying regular requests...")
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        try:
            response = session.get(BASE_URL, timeout=30)
            response.raise_for_status()
            page_content = response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error("Blocked by Cloudflare (403 Forbidden)")
                logger.error("Please install required dependencies: pip install cloudscraper selenium")
                logger.error("For selenium, you also need ChromeDriver installed")
            raise
    
    if not page_content:
        raise Exception("Failed to obtain page content with all methods")
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    downloaded_files = []
    found_files = {}
    
    # Parse the HTML structure: look for divs containing filename spans and gzip links
    for div in soup.find_all('div'):
        # Look for spans with filenames
        filename_span = div.find('span', class_='mr-10')
        if filename_span:
            filename_text = filename_span.text.strip()
            # Check if this is one of our required files
            gz_filename = f"{filename_text}.gz"
            if gz_filename in REQUIRED_FILES and gz_filename not in found_files:
                # Look for the gzip download link in the same div
                gzip_links = div.find_all('a', string='gzip')
                if gzip_links:
                    download_url = gzip_links[0].get('href')
                    if download_url:
                        found_files[gz_filename] = download_url
                        logger.info(f"Found {gz_filename} at URL: {download_url}")
    
    # Fallback method: look for any links containing our required filenames
    if not found_files:
        logger.warning("Primary parsing method failed, trying fallback method...")
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            for required_file in REQUIRED_FILES:
                if required_file in href and 'cdn.rebrickable.com' in href and required_file not in found_files:
                    found_files[required_file] = href
                    logger.info(f"Found {required_file} via fallback at URL: {href}")
    
    # Last resort: try to construct CDN URLs directly (they often follow a pattern)
    if not found_files:
        logger.warning("All parsing methods failed, trying direct CDN URL construction...")
        base_cdn_url = "https://cdn.rebrickable.com/media/downloads/"
        current_timestamp = time.time()
        
        for required_file in REQUIRED_FILES:
            if required_file not in found_files:
                # Try common timestamp patterns
                for timestamp_offset in [0, -3600, -7200, -86400]:  # current, 1h ago, 2h ago, 1d ago
                    test_timestamp = current_timestamp + timestamp_offset
                    test_url = f"{base_cdn_url}{required_file}?{test_timestamp}"
                    found_files[required_file] = test_url
                    logger.info(f"Constructed potential URL for {required_file}: {test_url}")
                    break  # Only try one timestamp per file
    
    logger.info(f"Found {len(found_files)} required files: {list(found_files.keys())}")
    
    if not found_files:
        logger.error("No required files found on the download page!")
        # Debug: Save the page content for inspection
        with open('temp/debug_page.html', 'w', encoding='utf-8') as f:
            f.write(page_content)
        logger.info("Saved page content to temp/debug_page.html for inspection")
        
        # Log some debug info about what we found
        all_spans = soup.find_all('span')
        logger.debug(f"Found {len(all_spans)} span elements")
        mr10_spans = soup.find_all('span', class_='mr-10')
        logger.debug(f"Found {len(mr10_spans)} spans with class 'mr-10'")
        if mr10_spans:
            logger.debug(f"Sample mr-10 span texts: {[s.text.strip() for s in mr10_spans[:5]]}")
        
        all_gzip_links = soup.find_all('a', string='gzip')
        logger.debug(f"Found {len(all_gzip_links)} 'gzip' links")
        if all_gzip_links:
            logger.debug(f"Sample gzip URLs: {[a.get('href') for a in all_gzip_links[:3]]}")
        
        raise Exception("No files were found! Check the Rebrickable website structure or blocking issues.")
    
    # Download each found file
    for gz_filename, file_url in found_files.items():
        logger.info(f"Processing {gz_filename} from URL: {file_url}")
        
        gz_path = os.path.join(TEMP_DIR, gz_filename)
        logger.info(f"Downloading {gz_filename} to {gz_path}")
        
        # Add delay between downloads to avoid rate limiting
        time.sleep(random.uniform(3, 7))
        
        # Retry mechanism for downloads
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Update headers for file download
                download_headers = session.headers.copy()
                download_headers.update({
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site',
                    'Referer': BASE_URL,
                })
                
                logger.info(f"Download attempt {attempt + 1}/{max_retries} for {gz_filename}")
                response = session.get(file_url, headers=download_headers, timeout=120)
                response.raise_for_status()
                break  # Success, exit retry loop
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {gz_filename}: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"Failed to download {gz_filename} after {max_retries} attempts")
                    continue  # Skip to next file
                else:
                    # Wait before retry with exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    logger.info(f"Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                    continue
        else:
            # If we get here, all retries failed
            continue
        
        # Process the downloaded file
        if len(response.content) == 0:
            logger.error(f"Downloaded file {gz_filename} is empty!")
            continue
        
        # Check if we got blocked (common blocking responses)
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type and len(response.content) < 10000:
            logger.error(f"Possibly blocked for {gz_filename} - got HTML response instead of file")
            logger.debug(f"Response content: {response.text[:500]}")
            continue
        
        try:
            with open(gz_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded {gz_filename} ({len(response.content)} bytes)")
            
            # Extract the gzip file
            csv_filename = gz_filename[:-3]  # Remove .gz extension
            csv_path = os.path.join(TEMP_DIR, csv_filename)
            
            with gzip.open(gz_path, 'rb') as f_in:
                with open(csv_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify the CSV file was created and has content
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                logger.info(f"Successfully extracted {gz_filename} to {csv_path} ({os.path.getsize(csv_path)} bytes)")
                downloaded_files.append(gz_filename)
                # Clean up the gz file after successful extraction
                os.remove(gz_path)
            else:
                logger.error(f"Extracted CSV file {csv_path} is empty or doesn't exist!")
                continue
                
        except gzip.BadGzipFile:
            logger.error(f"File {gz_filename} is not a valid gzip file!")
            # Save first 100 bytes for debugging
            try:
                with open(gz_path, 'rb') as f:
                    first_bytes = f.read(100)
                logger.debug(f"First 100 bytes: {first_bytes}")
            except:
                pass
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {gz_filename}: {e}")
            continue
    
    logger.info(f"Successfully downloaded and extracted {len(downloaded_files)} files: {downloaded_files}")
    
    if len(downloaded_files) == 0:
        raise Exception("No files were successfully downloaded! Check the Rebrickable website structure or blocking issues.")
    
    return downloaded_files

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
        downloaded_files = download_and_extract_files()
        
        logger.info("Generating SQL insert statements...")
        result = os.system('python3 generate_sql_insert.py')
        if result != 0:
            raise Exception("Failed to generate SQL insert statements")
        
        # Verify SQL files were created
        sql_files_created = []
        for csv_file, table_name in [('temp/sets.csv', 'sets'), ('temp/inventory_sets.csv', 'inventory_sets'), 
                                   ('temp/inventory_minifigs.csv', 'inventory_minifigs'), ('temp/minifigs.csv', 'minifigs'),
                                   ('temp/themes.csv', 'themes'), ('temp/inventories.csv', 'inventories')]:
            sql_file = f"sql_output/{table_name}_inserts.sql"
            if os.path.exists(sql_file) and os.path.getsize(sql_file) > 0:
                sql_files_created.append(sql_file)
        
        logger.info(f"Created SQL files: {sql_files_created}")
        if len(sql_files_created) == 0:
            raise Exception("No SQL files were generated! Check CSV file processing.")
        
        logger.info("Executing SQL files and updating database...")
        cursor, conn = execute_sql_files(db_host, db_user, db_pass, db_name, db_port)
        conn.close()
        
        logger.info("Cleaning up temporary files...")
        cleanup()
        
        logger.info("Data update completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()