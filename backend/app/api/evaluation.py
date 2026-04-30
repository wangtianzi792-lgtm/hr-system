from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.database import get_db
from app.models.evaluation import EvaluationCycle, EvaluationDimension, Evaluation, EvaluationScore, Evaluation360Report
from app.models.employee import Employee

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


# ==================== Schemas ====================
class DimensionCreate(BaseModel):
    name: str
    dimension_type: str
    description: Optional[str] = None
    weight: float = 1.0
    max_score: float = 5.0
    order_index: int = 0

class DimensionResponse(BaseModel):
    id: int
    name: str
    dimension_type: str
    description: Optional[str]
    weight: float
    max_score: float
    order_index: int
    is_active: bool
    
    class Config:
        from_attributes = True

class CycleCreate(BaseModel):
    name: str
    year: int
    period_type: str
    start_date: str
    end_date: str
    self_review_deadline: str
    peer_review_deadline: str
    manager_review_deadline: str
    remark: Optional[str] = None
    dimensions: List[DimensionCreate] = []

class CycleResponse(BaseModel):
    id: int
    name: str
    year: int
    period_type: str
    start_date: str
    end_date: str
    self_review_deadline: str
    peer_review_deadline: str
    manager_review_deadline: str
    status: str
    remark: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CycleWithDimensions(CycleResponse):
    dimensions: List[DimensionResponse] = []

class ScoreCreate(BaseModel):
    dimension_id: int
    score: float
    comment: Optional[str] = None

class EvaluationCreate(BaseModel):
    cycle_id: int
    reviewee_id: int
    reviewer_id: int
    review_type: str
    scores: List[ScoreCreate] = []
    self_review_text: Optional[str] = None

class EvaluationResponse(BaseModel):
    id: int
    cycle_id: int
    reviewee_id: int
    reviewer_id: int
    review_type: str
    status: str
    self_review_text: Optional[str]
    overall_score: Optional[float]
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EvaluationWithDetails(EvaluationResponse):
    reviewee_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    scores: List[dict] = []

class ReportResponse(BaseModel):
    id: int
    cycle_id: int
    employee_id: int
    employee_name: Optional[str] = None
    total_score: Optional[float]
    self_score: Optional[float]
    peer_score: Optional[float]
    manager_score: Optional[float]
    rank: Optional[int]
    generated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 考核周期管理 ====================
@router.get("/cycles", response_model=List[CycleResponse])
def list_cycles(
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取考核周期列表"""
    query = db.query(EvaluationCycle)
    if year:
        query = query.filter(EvaluationCycle.year == year)
    if status:
        query = query.filter(EvaluationCycle.status == status)
    return query.order_by(EvaluationCycle.created_at.desc()).all()


@router.get("/cycles/{cycle_id}", response_model=CycleWithDimensions)
def get_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """获取考核周期详情（含维度）"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    return cycle


@router.post("/cycles", response_model=CycleResponse)
def create_cycle(data: CycleCreate, db: Session = Depends(get_db)):
    """创建考核周期"""
    cycle = EvaluationCycle(
        name=data.name,
        year=data.year,
        period_type=data.period_type,
        start_date=data.start_date,
        end_date=data.end_date,
        self_review_deadline=data.self_review_deadline,
        peer_review_deadline=data.peer_review_deadline,
        manager_review_deadline=data.manager_review_deadline,
        remark=data.remark,
        status="draft"
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    
    # 创建维度
    for i, dim_data in enumerate(data.dimensions):
        dimension = EvaluationDimension(
            cycle_id=cycle.id,
            name=dim_data.name,
            dimension_type=dim_data.dimension_type,
            description=dim_data.description,
            weight=dim_data.weight,
            max_score=dim_data.max_score,
            order_index=i
        )
        db.add(dimension)
    db.commit()
    
    return cycle


@router.put("/cycles/{cycle_id}", response_model=CycleResponse)
def update_cycle(cycle_id: int, data: CycleCreate, db: Session = Depends(get_db)):
    """更新考核周期"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    
    cycle.name = data.name
    cycle.year = data.year
    cycle.period_type = data.period_type
    cycle.start_date = data.start_date
    cycle.end_date = data.end_date
    cycle.self_review_deadline = data.self_review_deadline
    cycle.peer_review_deadline = data.peer_review_deadline
    cycle.manager_review_deadline = data.manager_review_deadline
    cycle.remark = data.remark
    
    # 更新维度（先删除旧的）
    db.query(EvaluationDimension).filter(EvaluationDimension.cycle_id == cycle_id).delete()
    for i, dim_data in enumerate(data.dimensions):
        dimension = EvaluationDimension(
            cycle_id=cycle.id,
            name=dim_data.name,
            dimension_type=dim_data.dimension_type,
            description=dim_data.description,
            weight=dim_data.weight,
            max_score=dim_data.max_score,
            order_index=i
        )
        db.add(dimension)
    
    db.commit()
    return cycle


@router.put("/cycles/{cycle_id}/status")
def update_cycle_status(cycle_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    """更新考核周期状态（draft/active/completed/archived）"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    
    cycle.status = status
    db.commit()
    return {"message": f"考核周期状态已更新为 {status}"}


@router.delete("/cycles/{cycle_id}")
def delete_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """删除考核周期"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    
    db.delete(cycle)
    db.commit()
    return {"message": "考核周期已删除"}


# ==================== 考核评价管理 ====================
@router.get("/evaluations", response_model=List[EvaluationWithDetails])
def list_evaluations(
    cycle_id: Optional[int] = None,
    reviewee_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    review_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取考核评价列表"""
    query = db.query(Evaluation)
    if cycle_id:
        query = query.filter(Evaluation.cycle_id == cycle_id)
    if reviewee_id:
        query = query.filter(Evaluation.reviewee_id == reviewee_id)
    if reviewer_id:
        query = query.filter(Evaluation.reviewer_id == reviewer_id)
    if review_type:
        query = query.filter(Evaluation.review_type == review_type)
    if status:
        query = query.filter(Evaluation.status == status)
    
    evaluations = query.all()
    result = []
    for ev in evaluations:
        reviewee = db.query(Employee).filter(Employee.id == ev.reviewee_id).first()
        reviewer = db.query(Employee).filter(Employee.id == ev.reviewer_id).first()
        scores = db.query(EvaluationScore).filter(EvaluationScore.evaluation_id == ev.id).all()
        
        result.append({
            **{k: getattr(ev, k) for k in ['id', 'cycle_id', 'reviewee_id', 'reviewer_id', 'review_type', 'status', 'self_review_text', 'overall_score', 'submitted_at']},
            'reviewee_name': reviewee.name if reviewee else None,
            'reviewer_name': reviewer.name if reviewer else None,
            'scores': [{'dimension_id': s.dimension_id, 'score': s.score, 'comment': s.comment} for s in scores]
        })
    
    return result


@router.post("/evaluations", response_model=EvaluationResponse)
def create_evaluation(data: EvaluationCreate, db: Session = Depends(get_db)):
    """创建考核评价（提交评价）"""
    # 检查是否已存在
    existing = db.query(Evaluation).filter(
        Evaluation.cycle_id == data.cycle_id,
        Evaluation.reviewee_id == data.reviewee_id,
        Evaluation.reviewer_id == data.reviewer_id,
        Evaluation.review_type == data.review_type
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该评价已存在")
    
    # 计算总分
    total_score = 0
    total_weight = 0
    for score_data in data.scores:
        dim = db.query(EvaluationDimension).filter(EvaluationDimension.id == score_data.dimension_id).first()
        if dim:
            total_score += score_data.score * dim.weight
            total_weight += dim.weight
    
    overall_score = round(total_score / total_weight, 2) if total_weight > 0 else 0
    
    evaluation = Evaluation(
        cycle_id=data.cycle_id,
        reviewee_id=data.reviewee_id,
        reviewer_id=data.reviewer_id,
        review_type=data.review_type,
        status="submitted",
        self_review_text=data.self_review_text,
        overall_score=overall_score,
        submitted_at=datetime.now()
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 保存各维度得分
    for score_data in data.scores:
        score = EvaluationScore(
            evaluation_id=evaluation.id,
            dimension_id=score_data.dimension_id,
            score=score_data.score,
            comment=score_data.comment
        )
        db.add(score)
    db.commit()
    
    return evaluation


@router.get("/my-tasks")
def get_my_tasks(
    reviewer_id: int = Query(...),
    cycle_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取我的考核任务（待评价列表）"""
    query = db.query(Evaluation).filter(Evaluation.reviewer_id == reviewer_id)
    if cycle_id:
        query = query.filter(Evaluation.cycle_id == cycle_id)
    
    evaluations = query.all()
    result = []
    for ev in evaluations:
        reviewee = db.query(Employee).filter(Employee.id == ev.reviewee_id).first()
        cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == ev.cycle_id).first()
        
        result.append({
            'id': ev.id,
            'cycle_id': ev.cycle_id,
            'cycle_name': cycle.name if cycle else None,
            'reviewee_id': ev.reviewee_id,
            'reviewee_name': reviewee.name if reviewee else None,
            'review_type': ev.review_type,
            'status': ev.status,
            'deadline': {
                'self': cycle.self_review_deadline if cycle else None,
                'peer': cycle.peer_review_deadline if cycle else None,
                'manager': cycle.manager_review_deadline if cycle else None
            }.get(ev.review_type)
        })
    
    return result


# ==================== 360考核报告 ====================
@router.get("/reports/{cycle_id}", response_model=List[ReportResponse])
def get_cycle_reports(cycle_id: int, db: Session = Depends(get_db)):
    """获取考核周期的汇总报告"""
    reports = db.query(Evaluation360Report).filter(Evaluation360Report.cycle_id == cycle_id).all()
    
    result = []
    for r in reports:
        emp = db.query(Employee).filter(Employee.id == r.employee_id).first()
        result.append({
            **{k: getattr(r, k) for k in ['id', 'cycle_id', 'employee_id', 'total_score', 'self_score', 'peer_score', 'manager_score', 'rank', 'generated_at']},
            'employee_name': emp.name if emp else None
        })
    
    return result


@router.post("/generate-reports/{cycle_id}")
def generate_reports(cycle_id: int, db: Session = Depends(get_db)):
    """生成考核汇总报告"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    
    # 获取所有被考核人
    evaluations = db.query(Evaluation).filter(Evaluation.cycle_id == cycle_id).all()
    reviewee_ids = list(set([ev.reviewee_id for ev in evaluations]))
    
    # 删除旧报告
    db.query(Evaluation360Report).filter(Evaluation360Report.cycle_id == cycle_id).delete()
    
    reports_data = []
    for emp_id in reviewee_ids:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            continue
        
        # 获取该员工的所有评价
        emp_evaluations = [ev for ev in evaluations if ev.reviewee_id == emp_id]
        
        # 计算自评分数
        self_eval = [ev for ev in emp_evaluations if ev.review_type == 'self']
        self_score = self_eval[0].overall_score if self_eval else None
        
        # 计算互评平均分
        peer_evals = [ev for ev in emp_evaluations if ev.review_type == 'peer' and ev.overall_score]
        peer_score = round(sum([ev.overall_score for ev in peer_evals]) / len(peer_evals), 2) if peer_evals else None
        
        # 计算上级评价分数
        manager_evals = [ev for ev in emp_evaluations if ev.review_type == 'manager' and ev.overall_score]
        manager_score = round(sum([ev.overall_score for ev in manager_evals]) / len(manager_evals), 2) if manager_evals else None
        
        # 计算总分（权重：自评20%、互评40%、上级40%）
        scores = []
        weights = []
        if self_score:
            scores.append(self_score * 0.2)
            weights.append(0.2)
        if peer_score:
            scores.append(peer_score * 0.4)
            weights.append(0.4)
        if manager_score:
            scores.append(manager_score * 0.4)
            weights.append(0.4)
        
        total_score = round(sum(scores) / sum(weights), 2) if weights else None
        
        reports_data.append({
            'cycle_id': cycle_id,
            'employee_id': emp_id,
            'self_score': self_score,
            'peer_score': peer_score,
            'manager_score': manager_score,
            'total_score': total_score
        })
    
    # 按总分排序计算排名
    reports_data.sort(key=lambda x: x['total_score'] or 0, reverse=True)
    for i, data in enumerate(reports_data):
        data['rank'] = i + 1
        
        report = Evaluation360Report(**data)
        db.add(report)
    
    db.commit()
    
    return {"message": f"已生成 {len(reports_data)} 份考核报告"}


# ==================== 统计数据 ====================
@router.get("/stats/{cycle_id}")
def get_cycle_stats(cycle_id: int, db: Session = Depends(get_db)):
    """获取考核周期统计数据"""
    cycle = db.query(EvaluationCycle).filter(EvaluationCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="考核周期不存在")
    
    total_evaluations = db.query(Evaluation).filter(Evaluation.cycle_id == cycle_id).count()
    completed_evaluations = db.query(Evaluation).filter(
        Evaluation.cycle_id == cycle_id,
        Evaluation.status == 'submitted'
    ).count()
    
    # 按类型统计
    self_count = db.query(Evaluation).filter(Evaluation.cycle_id == cycle_id, Evaluation.review_type == 'self').count()
    peer_count = db.query(Evaluation).filter(Evaluation.cycle_id == cycle_id, Evaluation.review_type == 'peer').count()
    manager_count = db.query(Evaluation).filter(Evaluation.cycle_id == cycle_id, Evaluation.review_type == 'manager').count()
    
    # 获取维度列表
    dimensions = db.query(EvaluationDimension).filter(EvaluationDimension.cycle_id == cycle_id).all()
    
    return {
        'cycle_id': cycle_id,
        'cycle_name': cycle.name,
        'status': cycle.status,
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations,
        'completion_rate': round(completed_evaluations / total_evaluations * 100, 1) if total_evaluations > 0 else 0,
        'by_type': {
            'self': self_count,
            'peer': peer_count,
            'manager': manager_count
        },
        'dimensions_count': len(dimensions)
    }
