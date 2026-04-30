"""创建360考核相关表"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app', 'attendance.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查表是否已存在
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluation_cycles'")
if c.fetchone():
    print('Tables already exist')
else:
    # 创建考核周期表
    c.execute('''CREATE TABLE evaluation_cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        year INTEGER NOT NULL,
        period_type VARCHAR(20) NOT NULL,
        start_date VARCHAR(10) NOT NULL,
        end_date VARCHAR(10) NOT NULL,
        self_review_deadline VARCHAR(10) NOT NULL,
        peer_review_deadline VARCHAR(10) NOT NULL,
        manager_review_deadline VARCHAR(10) NOT NULL,
        status VARCHAR(20) DEFAULT 'draft',
        remark TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 创建考核维度表
    c.execute('''CREATE TABLE evaluation_dimensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        dimension_type VARCHAR(50) NOT NULL,
        description TEXT,
        weight REAL DEFAULT 1.0,
        max_score REAL DEFAULT 5.0,
        order_index INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES evaluation_cycles(id)
    )''')

    # 创建考核记录表
    c.execute('''CREATE TABLE evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL,
        reviewee_id INTEGER NOT NULL,
        reviewer_id INTEGER NOT NULL,
        review_type VARCHAR(20) NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        self_review_text TEXT,
        overall_score REAL,
        is_anonymous INTEGER DEFAULT 1,
        submitted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES evaluation_cycles(id),
        FOREIGN KEY (reviewee_id) REFERENCES employees(id),
        FOREIGN KEY (reviewer_id) REFERENCES employees(id)
    )''')

    # 创建考核维度得分表
    c.execute('''CREATE TABLE evaluation_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        dimension_id INTEGER NOT NULL,
        score REAL NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations(id),
        FOREIGN KEY (dimension_id) REFERENCES evaluation_dimensions(id)
    )''')

    # 创建360考核汇总报告表
    c.execute('''CREATE TABLE evaluation_360_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        total_score REAL,
        self_score REAL,
        peer_score REAL,
        manager_score REAL,
        rank INTEGER,
        report_data TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES evaluation_cycles(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )''')

    # 创建索引
    c.execute('CREATE INDEX idx_eval_cycle ON evaluations(cycle_id)')
    c.execute('CREATE INDEX idx_eval_reviewee ON evaluations(reviewee_id)')
    c.execute('CREATE INDEX idx_eval_reviewer ON evaluations(reviewer_id)')
    c.execute('CREATE INDEX idx_score_eval ON evaluation_scores(evaluation_id)')
    c.execute('CREATE INDEX idx_report_cycle ON evaluation_360_reports(cycle_id)')

    conn.commit()
    print('Tables created successfully!')

conn.close()
