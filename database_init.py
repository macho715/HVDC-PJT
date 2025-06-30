#!/usr/bin/env python3
"""
HVDC 루트 온톨로지 데이터베이스 초기화 스크립트
MACHO-GPT v3.4-mini 표준 준수
"""

import sqlite3
import os
from datetime import datetime

def init_hvdc_database():
    """HVDC 루트 온톨로지 데이터베이스 초기화"""
    
    print('🔧 HVDC 루트 온톨로지 데이터베이스 초기화 시작...')
    print(f'📅 시작 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 데이터베이스 연결 및 생성
    db_path = 'data/hvdc.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Items 테이블 생성 (확장된 스키마)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        hvdc_code TEXT PRIMARY KEY,
        vendor TEXT NOT NULL,
        category TEXT,
        weight REAL DEFAULT 0,
        location TEXT,
        status TEXT DEFAULT 'UNKNOWN',
        risk_level TEXT DEFAULT 'NORMAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        handling_fee REAL DEFAULT 0,
        cbm REAL DEFAULT 0,
        package_count INTEGER DEFAULT 1
    )
    ''')
    
    # Warehouses 테이블 생성 (확장된 스키마)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS warehouses (
        name TEXT PRIMARY KEY,
        warehouse_type TEXT NOT NULL,
        capacity_sqm REAL DEFAULT 0,
        current_utilization REAL DEFAULT 0,
        handling_fee REAL DEFAULT 0,
        location_code TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Transactions 테이블 생성 (WAREHOUSE 시스템 연동용)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hvdc_code TEXT,
        transaction_type TEXT,
        warehouse_name TEXT,
        quantity INTEGER DEFAULT 0,
        amount REAL DEFAULT 0,
        transaction_date TIMESTAMP,
        flow_code INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hvdc_code) REFERENCES items (hvdc_code),
        FOREIGN KEY (warehouse_name) REFERENCES warehouses (name)
    )
    ''')
    
    # System Status 테이블 생성 (시스템 모니터링용)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_status (
        status_id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_name TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence_level REAL DEFAULT 0,
        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        details TEXT
    )
    ''')
    
    # 인덱스 생성 (성능 최적화)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_vendor ON items(vendor)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_location ON items(location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
    
    # 변경사항 커밋
    conn.commit()
    
    # 테이블 검증
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f'✅ 생성된 테이블: {len(tables)}개')
    for table in tables:
        print(f'   - {table[0]}')
    
    # 인덱스 검증
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
    indexes = cursor.fetchall()
    print(f'📊 생성된 인덱스: {len(indexes)}개')
    for index in indexes:
        print(f'   - {index[0]}')
    
    # 데이터베이스 파일 크기 확인
    file_size = os.path.getsize(db_path)
    print(f'📦 데이터베이스 파일 크기: {file_size} bytes')
    
    # 초기 시스템 상태 입력
    cursor.execute('''
    INSERT OR REPLACE INTO system_status 
    (system_name, status, confidence_level, details)
    VALUES ('ROOT_ONTOLOGY', 'INITIALIZED', 95.0, 'Database schema created successfully')
    ''')
    
    conn.commit()
    conn.close()
    
    print('🎯 루트 온톨로지 데이터베이스 초기화 완료!')
    print(f'📅 완료 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    return True

if __name__ == "__main__":
    success = init_hvdc_database()
    if success:
        print('✅ 데이터베이스 초기화 성공!')
    else:
        print('❌ 데이터베이스 초기화 실패!') 