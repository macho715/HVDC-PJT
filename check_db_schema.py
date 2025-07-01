#!/usr/bin/env python3
"""
🔍 Database Schema Checker
Check database table structure and columns
"""

import sqlite3

def check_database_schema():
    """Check database schema and columns"""
    try:
        conn = sqlite3.connect('hvdc_ontology_system/data/hvdc.db')
        
        # Get table names
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = conn.execute(tables_query).fetchall()
        
        print("📊 Database Tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Get columns for items table
        if ('items',) in tables:
            columns_query = "PRAGMA table_info(items)"
            columns = conn.execute(columns_query).fetchall()
            
            print(f"\n📋 Items Table Columns:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        
        # Sample data
        sample_query = "SELECT * FROM items LIMIT 3"
        samples = conn.execute(sample_query).fetchall()
        
        print(f"\n📄 Sample Data (first 3 rows):")
        if columns:
            column_names = [col[1] for col in columns]
            print(f"Columns: {column_names}")
            for i, row in enumerate(samples):
                print(f"Row {i+1}: {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database_schema() 