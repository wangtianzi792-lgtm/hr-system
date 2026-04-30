-- 2026年海昌花名册数据表
CREATE TABLE IF NOT EXISTS roster (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 基本信息
    序号 VARCHAR(20),
    离职日期 DATE,
    离职原因 VARCHAR(200),
    档案号 VARCHAR(50),
    厂区 VARCHAR(50),
    工号 VARCHAR(20) NOT NULL,
    姓名 VARCHAR(50) NOT NULL,
    人员类别 VARCHAR(50),
    事业部 VARCHAR(100),
    部门 VARCHAR(100),
    工序 VARCHAR(100),
    岗位 VARCHAR(100),
    -- 审计口径
    部门_审计口径 VARCHAR(100),
    岗位_审计口径 VARCHAR(100),
    职务级别 VARCHAR(50),
    -- 入职信息
    入职时间 DATE,
    试用到期日 DATE,
    联系电话 VARCHAR(50),
    紧急联系电话 VARCHAR(50),
    -- 身份信息
    身份证号 VARCHAR(18),
    性别 VARCHAR(10),
    出生日期 DATE,
    年龄 INTEGER,
    民族 VARCHAR(20),
    工龄 VARCHAR(20),
    用工形式 VARCHAR(50),
    体检类别 VARCHAR(100),
    -- 教育信息
    员工 VARCHAR(50),
    文化程度 VARCHAR(50),
    学历工资 VARCHAR(50),
    毕业院校及专业 VARCHAR(200),
    -- 居住信息
    户籍地址 VARCHAR(300),
    扬州暂住地 VARCHAR(300),
    -- 合同信息
    合同起始 DATE,
    合同终止 DATE,
    签定 VARCHAR(10),
    公积金标准 VARCHAR(50),
    其他 VARCHAR(200),
    工龄工资 VARCHAR(50),
    -- 元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);