-- 初始化数据库
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建初始管理员账户（密码: admin123）
-- 实际使用时应该使用 bcrypt 加密
INSERT INTO users (username, email, hashed_password, full_name, is_superuser, role)
VALUES ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', '系统管理员', true, 'admin');

-- 创建示例部门
INSERT INTO departments (name, code, description, sort_order)
VALUES 
  ('技术部', 'TECH', '负责技术研发', 1),
  ('销售部', 'SALE', '负责产品销售', 2),
  ('人事部', 'HR', '负责人事管理', 3),
  ('财务部', 'FIN', '负责财务管理', 4);

-- 创建示例员工
INSERT INTO employees (employee_no, name, gender, phone, email, department_id, position, entry_date, status)
VALUES 
  ('E001', '张三', '男', '13800138001', 'zhangsan@example.com', 1, '高级工程师', '2023-01-15', 'active'),
  ('E002', '李四', '女', '13800138002', 'lisi@example.com', 2, '销售经理', '2023-03-20', 'active'),
  ('E003', '王五', '男', '13800138003', 'wangwu@example.com', 3, '人事专员', '2023-06-10', 'active');
