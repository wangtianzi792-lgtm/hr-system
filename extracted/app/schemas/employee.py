from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class EmployeeBase(BaseModel):
    employee_no: str = Field(..., min_length=1, max_length=20, description="工号")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    id_card: Optional[str] = Field(None, description="身份证号")
    department_id: Optional[int] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, description="职位")
    entry_date: Optional[date] = Field(None, description="入职日期")
    card_no: Optional[str] = Field(None, description="卡号")
    
    # 海昌花名册扩展字段
    archive_no: Optional[str] = Field(None, description="档案号")
    factory: Optional[str] = Field(None, description="厂区")
    person_type: Optional[str] = Field(None, description="人员类别")
    business_unit: Optional[str] = Field(None, description="事业部")
    process: Optional[str] = Field(None, description="工序")
    medical_exam_type: Optional[str] = Field(None, description="体检—工种")
    medical_exam_factor: Optional[str] = Field(None, description="体检—有害因素")
    dept_audit: Optional[str] = Field(None, description="部门—审计口径")
    position_audit: Optional[str] = Field(None, description="岗位—审计口径")
    job_level: Optional[str] = Field(None, description="职务级别")
    probation_end_date: Optional[date] = Field(None, description="试用到期日")
    emergency_phone: Optional[str] = Field(None, description="紧急联系电话")
    birth_date: Optional[date] = Field(None, description="出生日期")
    age: Optional[int] = Field(None, description="年龄")
    ethnicity: Optional[str] = Field(None, description="民族")
    work_years: Optional[str] = Field(None, description="工龄")
    employment_type: Optional[str] = Field(None, description="用工形式")
    medical_category: Optional[str] = Field(None, description="体检类别")
    employee_group: Optional[str] = Field(None, description="员工分组")
    education: Optional[str] = Field(None, description="文化程度")
    education_salary: Optional[str] = Field(None, description="学历工资")
    school_major: Optional[str] = Field(None, description="毕业院校及专业")
    household_address: Optional[str] = Field(None, description="户籍地址")
    temporary_address: Optional[str] = Field(None, description="扬州暂住地")
    contract_start: Optional[date] = Field(None, description="合同起始")
    contract_end: Optional[date] = Field(None, description="合同终止")
    contract_signed: Optional[str] = Field(None, description="签定")
    provident_fund: Optional[str] = Field(None, description="公积金（标准）")
    retirement_date: Optional[date] = Field(None, description="退休人员日期")
    work_years_salary: Optional[str] = Field(None, description="工龄工资")
    training: Optional[str] = Field(None, description="参加培训")


class EmployeeCreate(EmployeeBase):
    role_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    employee_no: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    entry_date: Optional[date] = None
    card_no: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    
    # 海昌花名册扩展字段
    archive_no: Optional[str] = None
    factory: Optional[str] = None
    person_type: Optional[str] = None
    business_unit: Optional[str] = None
    process: Optional[str] = None
    medical_exam_type: Optional[str] = None
    medical_exam_factor: Optional[str] = None
    dept_audit: Optional[str] = None
    position_audit: Optional[str] = None
    job_level: Optional[str] = None
    probation_end_date: Optional[date] = None
    emergency_phone: Optional[str] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    work_years: Optional[str] = None
    employment_type: Optional[str] = None
    medical_category: Optional[str] = None
    employee_group: Optional[str] = None
    education: Optional[str] = None
    education_salary: Optional[str] = None
    school_major: Optional[str] = None
    household_address: Optional[str] = None
    temporary_address: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    contract_signed: Optional[str] = None
    provident_fund: Optional[str] = None
    retirement_date: Optional[date] = None
    work_years_salary: Optional[str] = None
    training: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    status: str = "active"
    zk_user_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    department_name: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    total: int
    items: list[EmployeeResponse]
