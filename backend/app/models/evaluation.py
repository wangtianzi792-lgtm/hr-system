from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class EvaluationCycle(Base):
    """考核周期"""
    __tablename__ = "evaluation_cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="周期名称，如：2025年度360考核")
    year = Column(Integer, nullable=False, comment="考核年份")
    period_type = Column(String(20), nullable=False, comment="考核类型：annual/half_year/quarter/monthly")
    start_date = Column(String(10), nullable=False, comment="开始日期 YYYY-MM-DD")
    end_date = Column(String(10), nullable=False, comment="结束日期 YYYY-MM-DD")
    self_review_deadline = Column(String(10), nullable=False, comment="自评截止日期")
    peer_review_deadline = Column(String(10), nullable=False, comment="互评截止日期")
    manager_review_deadline = Column(String(10), nullable=False, comment="上级评价截止日期")
    status = Column(String(20), default="draft", comment="draft/active/completed/archived")
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    dimensions = relationship("EvaluationDimension", back_populates="cycle")
    evaluations = relationship("Evaluation", back_populates="cycle")


class EvaluationDimension(Base):
    """考核维度"""
    __tablename__ = "evaluation_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("evaluation_cycles.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="维度名称，如：专业能力")
    dimension_type = Column(String(50), nullable=False, comment="类型：professional/teamwork/leadership/innovation/quality/other")
    description = Column(Text, nullable=True, comment="维度说明")
    weight = Column(Float, default=1.0, comment="权重，默认1.0")
    max_score = Column(Float, default=5.0, comment="最高分")
    order_index = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    cycle = relationship("EvaluationCycle", back_populates="dimensions")
    scores = relationship("EvaluationScore", back_populates="dimension")


class Evaluation(Base):
    """考核记录"""
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("evaluation_cycles.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="被考核人")
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="评价人")
    review_type = Column(String(20), nullable=False, comment="自评self/同级互评peer/上级评价manager")
    status = Column(String(20), default="pending", comment="pending/submitted/completed")
    self_review_text = Column(Text, nullable=True, comment="自评文字")
    overall_score = Column(Float, nullable=True, comment="综合得分")
    is_anonymous = Column(Boolean, default=True, comment="是否匿名（互评匿名）")
    submitted_at = Column(DateTime, nullable=True, comment="提交时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cycle = relationship("EvaluationCycle", back_populates="evaluations")
    reviewee = relationship("Employee", foreign_keys=[reviewee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    scores = relationship("EvaluationScore", back_populates="evaluation")


class EvaluationScore(Base):
    """考核维度得分"""
    __tablename__ = "evaluation_scores"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("evaluation_dimensions.id"), nullable=False)
    score = Column(Float, nullable=False, comment="得分")
    comment = Column(Text, nullable=True, comment="维度评价")
    created_at = Column(DateTime, server_default=func.now())

    evaluation = relationship("Evaluation", back_populates="scores")
    dimension = relationship("EvaluationDimension", back_populates="scores")


class Evaluation360Report(Base):
    """360考核汇总报告"""
    __tablename__ = "evaluation_360_reports"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("evaluation_cycles.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="被考核人")
    total_score = Column(Float, nullable=True, comment="综合得分")
    self_score = Column(Float, nullable=True, comment="自评得分")
    peer_score = Column(Float, nullable=True, comment="互评得分")
    manager_score = Column(Float, nullable=True, comment="上级评价得分")
    rank = Column(Integer, nullable=True, comment="本周期内排名")
    report_data = Column(Text, nullable=True, comment="完整报告JSON快照")
    generated_at = Column(DateTime, server_default=func.now())

    cycle = relationship("EvaluationCycle")
    employee = relationship("Employee")
