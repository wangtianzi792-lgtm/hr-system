# -*- coding: utf-8 -*-
"""360考核模块种子数据"""
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.evaluation import (
    EvaluationCycle, EvaluationDimension,
    Evaluation, EvaluationScore, Evaluation360Report
)
from app.models.employee import Employee

db = SessionLocal()
try:
    existing = db.query(EvaluationCycle).first()
    if existing:
        print("Evaluation data already exists. Skipping.")
    else:
        # 先创建考核周期
        cycle = EvaluationCycle(
            name="2026年第一季度考核",
            year=2026,
            period_type="quarterly",
            start_date="2026-01-01",
            end_date="2026-03-31",
            self_review_deadline="2026-04-10",
            peer_review_deadline="2026-04-15",
            manager_review_deadline="2026-04-20",
            status="active",
            remark="2026年Q1季度360度考核"
        )
        db.add(cycle)
        db.flush()
        print(f"Created cycle: {cycle.name} (id={cycle.id})")
        
        # 创建考核维度（关联到 cycle）
        dimensions_data = [
            {"cycle_id": cycle.id, "name": "工作业绩", "dimension_type": "performance", "description": "完成工作的数量、质量和效率", "weight": 0.40, "max_score": 5.0, "order_index": 1},
            {"cycle_id": cycle.id, "name": "工作能力", "dimension_type": "ability", "description": "专业知识、技能、解决问题的能力", "weight": 0.30, "max_score": 5.0, "order_index": 2},
            {"cycle_id": cycle.id, "name": "工作态度", "dimension_type": "attitude", "description": "责任心、执行力、团队协作", "weight": 0.20, "max_score": 5.0, "order_index": 3},
            {"cycle_id": cycle.id, "name": "职业道德", "dimension_type": "ethics", "description": "廉洁自律、遵守制度、诚实守信", "weight": 0.10, "max_score": 5.0, "order_index": 4},
        ]
        
        dims = []
        for d in dimensions_data:
            dim = EvaluationDimension(**d)
            db.add(dim)
            dims.append(dim)
        
        db.flush()
        print(f"Created {len(dims)} dimensions")
        
        # 为前20名员工创建考核记录
        employees = db.query(Employee).filter(Employee.is_active == True).limit(20).all()
        print(f"Found {len(employees)} employees")
        
        for emp in employees:
            # 自评
            self_eval = Evaluation(
                cycle_id=cycle.id,
                reviewee_id=emp.id,
                reviewer_id=emp.id,
                review_type="self",
                status="completed",
                self_review_text="本人在本季度认真履行职责，完成了各项工作任务。"
            )
            db.add(self_eval)
            db.flush()
            
            for dim in dims:
                score = EvaluationScore(
                    evaluation_id=self_eval.id,
                    dimension_id=dim.id,
                    score=round(3.0 + (emp.id % 10) * 0.2, 1)
                )
                db.add(score)
            
            # 主管评
            if emp.department_id:
                manager = db.query(Employee).filter(
                    Employee.department_id == emp.department_id,
                    Employee.id != emp.id
                ).first()
                if manager:
                    manager_eval = Evaluation(
                        cycle_id=cycle.id,
                        reviewee_id=emp.id,
                        reviewer_id=manager.id,
                        review_type="manager",
                        status="completed"
                    )
                    db.add(manager_eval)
                    db.flush()
                    
                    for dim in dims:
                        score = EvaluationScore(
                            evaluation_id=manager_eval.id,
                            dimension_id=dim.id,
                            score=round(3.2 + (emp.id % 12) * 0.15, 1)
                        )
                        db.add(score)
        
        db.commit()
        print(f"\nSeed data created successfully!")
        print(f"  Cycle: {cycle.name}")
        print(f"  Dimensions: {len(dims)}")
        print(f"  Employees evaluated: {len(employees)}")
        
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
