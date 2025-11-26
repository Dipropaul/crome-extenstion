"""
Database migration script to add new fields to existing leads database
"""
import sqlite3
import shutil
from datetime import datetime

# Backup the database first
backup_file = f'leads_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
try:
    shutil.copy('leads.db', backup_file)
    print(f"Database backed up to: {backup_file}")
except Exception as e:
    print(f"Warning: Could not backup database: {e}")

# Connect to database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(leads)")
existing_columns = [row[1] for row in cursor.fetchall()]
print(f"\nExisting columns: {existing_columns}")

# New columns to add
new_columns = {
    'email': 'TEXT',
    'phone': 'TEXT',
    'logo_url': 'TEXT',
    'favicon_url': 'TEXT',
    'twitter_handle': 'TEXT',
    'linkedin_url': 'TEXT',
    'facebook_url': 'TEXT',
    'instagram_url': 'TEXT',
    'contact_page': 'TEXT',
    'industry_keywords': 'TEXT',
    'language': 'TEXT'
}

# Add missing columns
added_columns = []
for col_name, col_type in new_columns.items():
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE leads ADD COLUMN {col_name} {col_type}')
            added_columns.append(col_name)
            print(f"✓ Added column: {col_name}")
        except Exception as e:
            print(f"✗ Error adding {col_name}: {e}")

conn.commit()

# Verify new schema
cursor.execute("PRAGMA table_info(leads)")
new_columns_list = [row[1] for row in cursor.fetchall()]
print(f"\nUpdated columns: {new_columns_list}")

# Show current leads count
cursor.execute("SELECT COUNT(*) FROM leads")
count = cursor.fetchone()[0]
print(f"\nTotal leads in database: {count}")

conn.close()

if added_columns:
    print(f"\n✓ Migration completed! Added {len(added_columns)} new columns.")
    print("  Note: Existing leads will have NULL/empty values for new fields.")
    print("  Re-scrape websites to populate new data.")
else:
    print("\n✓ Database already up to date!")
