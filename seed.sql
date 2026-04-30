-- Seed demo data for attendance system
-- Department: 行政部, 技术部, 销售部, 生产部
INSERT OR IGNORE INTO departments (id, name, code, manager_id, is_active, created_at, updated_at)
VALUES 
(1, '行政部', 'ADMIN', NULL, 1, datetime('now'), datetime('now')),
(2, '技术部', 'TECH', NULL, 1, datetime('now'), datetime('now')),
(3, '销售部', 'SALES', NULL, 1, datetime('now'), datetime('now')),
(4, '生产部', 'PROD', NULL, 1, datetime('now'), datetime('now'));

-- Employees
INSERT OR IGNORE INTO employees (id, employee_no, name, gender, phone, department_id, position, entry_date, status, is_active, zk_user_id, zk_password, card_no, created_at, updated_at)
VALUES 
(1, 'E001', '张伟', '男', '13812340001', 2, 'Java开发工程师', date('now', '-180 days'), 'active', 1, 1, '123456', '60001001', datetime('now'), datetime('now')),
(2, 'E002', '李娜', '女', '13812340002', 2, '前端开发工程师', date('now', '-90 days'), 'active', 1, 2, '123456', '60001002', datetime('now'), datetime('now')),
(3, 'E003', '王强', '男', '13812340003', 3, '销售经理', date('now', '-365 days'), 'active', 1, 3, '123456', '60001003', datetime('now'), datetime('now')),
(4, 'E004', '陈静', '女', '13812340004', 1, '行政主管', date('now', '-400 days'), 'active', 1, 4, '123456', '60001004', datetime('now'), datetime('now')),
(5, 'E005', '刘洋', '男', '13812340005', 4, '生产主管', date('now', '-200 days'), 'active', 1, 5, '123456', '60001005', datetime('now'), datetime('now')),
(6, 'E006', '赵敏', '女', '13812340006', 2, '测试工程师', date('now', '-60 days'), 'active', 1, 6, '123456', '60001006', datetime('now'), datetime('now')),
(7, 'E007', '周涛', '男', '13812340007', 3, '销售代表', date('now', '-150 days'), 'active', 1, 7, '123456', '60001007', datetime('now'), datetime('now')),
(8, 'E008', '吴娟', '女', '13812340008', 1, '人事专员', date('now', '-100 days'), 'active', 1, 8, '123456', '60001008', datetime('now'), datetime('now'));

-- Shifts
INSERT OR IGNORE INTO shifts (id, name, shift_type, check_in_start, check_in_end, check_out_start, check_out_end, work_hours, color, is_active, remark, created_at, updated_at)
VALUES 
(1, '标准班', 'day', '08:30:00', '09:30:00', '17:30:00', '18:30:00', '8.5', '#409EFF', 1, '标准工作日', datetime('now'), datetime('now')),
(2, '早班', 'day', '07:00:00', '08:00:00', '15:00:00', '16:00:00', '8.0', '#67C23A', 1, '早班', datetime('now'), datetime('now')),
(3, '晚班', 'day', '14:00:00', '15:00:00', '22:00:00', '23:00:00', '8.0', '#E6A23C', 1, '晚班', datetime('now'), datetime('now'));

-- Generate attendance records for last 30 days
-- For each employee, generate records for last 30 days with some late/early/absent
WITH RECURSIVE days(d) AS (
    SELECT date('now', '-30 days')
    UNION ALL
    SELECT date(d, '+1 day') FROM days WHERE d < date('now')
),
employee_ids AS (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 
                 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8)
INSERT OR IGNORE INTO attendance_records (employee_id, device_id, punch_date, punch_time, punch_type, verify_type, status, raw_data, created_at)
SELECT 
    e.id,
    NULL,
    d.d,
    CASE WHEN (ABS(RANDOM()) % 10) < 7 THEN
        -- normal: check in around 8:30-9:00, check out around 17:30-18:00
        datetime(d.d || ' ' || 
            CASE WHEN e.id IN (1,2) THEN '08:35:00' WHEN e.id IN (3,4) THEN '08:45:00' ELSE '08:50:00' END ||
            printf(' +%d minutes', ABS(RANDOM()) % 20))
    ELSE
        datetime(d.d || ' 09:15:00')
    END,
    'check_in',
    1,
    CASE WHEN (ABS(RANDOM()) % 10) < 8 THEN 'normal' ELSE 'late' END,
    'seed_data',
    datetime('now')
FROM days d, employee_ids e
WHERE strftime('%w', d.d) NOT IN ('0', '6')
  AND d.d >= date('now', '-30 days') AND d.d <= date('now');

-- Add check_out records
INSERT OR IGNORE INTO attendance_records (employee_id, device_id, punch_date, punch_time, punch_type, verify_type, status, raw_data, created_at)
SELECT 
    e.id,
    NULL,
    d.d,
    CASE WHEN (ABS(RANDOM()) % 10) < 7 THEN
        datetime(d.d || ' ' || 
            CASE WHEN e.id IN (1,2) THEN '18:05:00' WHEN e.id IN (3,4) THEN '17:50:00' ELSE '17:35:00' END ||
            printf(' +%d minutes', ABS(RANDOM()) % 15))
    ELSE
        datetime(d.d || ' 17:20:00')
    END,
    'check_out',
    1,
    CASE WHEN (ABS(RANDOM()) % 10) < 9 THEN 'normal' ELSE 'early' END,
    'seed_data',
    datetime('now')
FROM days d, employee_ids e
WHERE strftime('%w', d.d) NOT IN ('0', '6')
  AND d.d >= date('now', '-30 days') AND d.d <= date('now');