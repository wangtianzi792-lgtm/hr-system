from sqlalchemy import Column, Integer, String, Date, DateTime
from app.core.database import Base


class Roster(Base):
    __tablename__ = "roster"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 基本信息
    序号 = Column(String(20))
    档案号 = Column(String(50))
    厂区 = Column(String(50))
    工号 = Column(String(20), nullable=False)
    姓名 = Column(String(50), nullable=False)
    人员类别 = Column(String(50))
    事业部 = Column(String(100))
    部门 = Column(String(100))
    工序 = Column(String(100))
    岗位 = Column(String(100))
    # 审计口径
    部门_审计口径 = Column(String(100))
    岗位_审计口径 = Column(String(100))
    职务级别 = Column(String(50))
    # 入职信息
    入职时间 = Column(Date)
    试用到期日 = Column(Date)
    联系电话 = Column(String(50))
    紧急联系电话 = Column(String(50))
    # 身份信息
    身份证号 = Column(String(18))
    性别 = Column(String(10))
    出生日期 = Column(Date)
    年龄 = Column(Integer)
    民族 = Column(String(20))
    工龄 = Column(String(20))
    用工形式 = Column(String(50))
    体检类别 = Column(String(100))
    # 教育信息
    员工 = Column(String(50))
    文化程度 = Column(String(50))
    学历工资 = Column(String(50))
    毕业院校及专业 = Column(String(200))
    # 居住信息
    户籍地址 = Column(String(300))
    扬州暂住地 = Column(String(300))
    # 合同信息
    合同起始 = Column(Date)
    合同终止 = Column(Date)
    签定 = Column(String(10))
    公积金标准 = Column(String(50))
    其他 = Column(String(200))
    工龄工资 = Column(String(50))
    created_at = Column(DateTime)