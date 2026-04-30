from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String(20), unique=True, nullable=False, comment="工号")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    id_card = Column(String(18), nullable=True, comment="身份证号")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    position = Column(String(100), nullable=True, comment="职位")
    entry_date = Column(Date, nullable=True, comment="入职日期")
    status = Column(String(20), default="active", comment="状态: active/leave")
    
    # 考勤机相关
    zk_user_id = Column(Integer, nullable=True, comment="考勤机用户ID")
    zk_password = Column(String(20), nullable=True, comment="考勤机密码")
    card_no = Column(String(50), nullable=True, comment="卡号")
    
    # 海昌花名册扩展字段
    archive_no = Column(String(50), nullable=True, comment="档案号")
    factory = Column(String(50), nullable=True, comment="厂区")
    person_type = Column(String(50), nullable=True, comment="人员类别")
    business_unit = Column(String(100), nullable=True, comment="事业部")
    process = Column(String(100), nullable=True, comment="工序")
    medical_exam_type = Column(String(100), nullable=True, comment="体检—工种")
    medical_exam_factor = Column(String(100), nullable=True, comment="体检—有害因素")
    dept_audit = Column(String(100), nullable=True, comment="部门—审计口径")
    position_audit = Column(String(100), nullable=True, comment="岗位—审计口径")
    job_level = Column(String(50), nullable=True, comment="职务级别")
    probation_end_date = Column(Date, nullable=True, comment="试用到期日")
    emergency_phone = Column(String(20), nullable=True, comment="紧急联系电话")
    birth_date = Column(Date, nullable=True, comment="出生日期")
    age = Column(Integer, nullable=True, comment="年龄")
    ethnicity = Column(String(20), nullable=True, comment="民族")
    work_years = Column(String(20), nullable=True, comment="工龄")
    employment_type = Column(String(50), nullable=True, comment="用工形式")
    medical_category = Column(String(50), nullable=True, comment="体检类别")
    employee_group = Column(String(50), nullable=True, comment="员工分组")
    education = Column(String(50), nullable=True, comment="文化程度")
    education_salary = Column(String(50), nullable=True, comment="学历工资")
    school_major = Column(String(200), nullable=True, comment="毕业院校及专业")
    household_address = Column(String(300), nullable=True, comment="户籍地址")
    temporary_address = Column(String(300), nullable=True, comment="扬州暂住地")
    contract_start = Column(Date, nullable=True, comment="合同起始")
    contract_end = Column(Date, nullable=True, comment="合同终止")
    contract_signed = Column(String(10), nullable=True, comment="签定")
    provident_fund = Column(String(50), nullable=True, comment="公积金（标准）")
    retirement_date = Column(Date, nullable=True, comment="退休人员日期")
    work_years_salary = Column(String(50), nullable=True, comment="工龄工资")
    training = Column(String(200), nullable=True, comment="参加培训")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id], overlaps="manager")
    attendance_records = relationship("AttendanceRecord", back_populates="employee")
    shift_assignments = relationship("ShiftAssignment", back_populates="employee")
    schedule_records = relationship("ScheduleRecord", back_populates="employee")
