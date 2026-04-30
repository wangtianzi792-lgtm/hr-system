"""
招商银行薪福通（XFT）打卡数据拉取客户端
已验证可用格式：
- POST https://api.cmbchina.com/atd/prd/xft-atn/click/query
- Headers: appId, access_token
- Body: beginDate, endDate, pageSize
"""
import requests
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# ============ 配置 ============
XFT_APP_ID = "e2c8d6b0-125b-420d-9248-681e3b3a6a4b"
XFT_AUTH_SECRET = "00b6056f5fc6df8def01cac77cf97f25dd84ccfd8121083a4252ee71b70a4148ee"
XFT_COMPANY_CODE = "A0001"
XFT_USER_CODE = "A0001"

# 生产环境
XFT_TOKEN_URL = "https://api.cmbchina.com/common/api/common/xft-login-new/v1/access_token"
XFT_PUNCH_URL = "https://api.cmbchina.com/atd/prd/xft-atn/click/query"

DB_PATH = os.path.join(os.path.dirname(__file__), "attendance.db")


def get_access_token() -> Optional[str]:
    """
    获取 access_token
    POST 请求，appId 在 body 和 header 都要传
    """
    payload = {
        "appId": XFT_APP_ID,
        "AuthoritySecret": XFT_AUTH_SECRET,
        "CompanyCode": XFT_COMPANY_CODE,
        "UserCode": XFT_USER_CODE
    }
    headers = {
        "Content-Type": "application/json",
        "appId": XFT_APP_ID
    }
    try:
        resp = requests.post(XFT_TOKEN_URL, headers=headers, json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200 and "token" in data:
            return data["token"]
        print(f"[Token失败] {resp.status_code}: {data}")
        return None
    except Exception as e:
        print(f"[Token异常] {e}")
        return None


def pull_punch_records(begin_date: str, end_date: str, page_size: int = 1000):
    """
    拉取打卡记录
    begin_date / end_date: YYYY-MM-DD
    返回: (records_list, total_count) 或 (None, error_msg)
    """
    token = get_access_token()
    if not token:
        return None, "Token获取失败，请确认服务器IP已加白名单"

    headers = {
        "Content-Type": "application/json",
        "appId": XFT_APP_ID,
        "access_token": token
    }
    payload = {
        "beginDate": begin_date,
        "endDate": end_date,
        "pageSize": page_size
    }

    try:
        resp = requests.post(XFT_PUNCH_URL, headers=headers, json=payload, timeout=30)
        data = resp.json()

        if data.get("returnCode") == "SUC0000":
            records = data.get("body", {}).get("clickRecordDtoList", [])
            total = data.get("body", {}).get("page", {}).get("total", 0)
            return records, total
        else:
            return None, data.get("errorMsg", f"接口错误: {data}")
    except Exception as e:
        return None, f"请求异常: {e}"


def save_punch_records(records: list):
    """保存打卡记录到数据库 attendance_records 表"""
    if not records:
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 建表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            record_number TEXT PRIMARY KEY,
            staff_number TEXT,
            staff_seq TEXT,
            staff_name TEXT,
            org_seq TEXT,
            click_time TEXT,
            click_source TEXT,
            click_device TEXT,
            click_date TEXT,
            click_place TEXT,
            remark TEXT,
            machine_number TEXT,
            work_location TEXT,
            synced_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # 插入或更新
    inserted = 0
    for r in records:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO attendance_records
                (record_number, staff_number, staff_seq, staff_name, org_seq,
                 click_time, click_source, click_device, click_date,
                 click_place, remark, machine_number, work_location, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                r.get("recordNumber"),
                r.get("staffNumber"),
                r.get("staffSeq"),
                r.get("staffName"),
                r.get("orgSeq"),
                r.get("clickTime"),
                r.get("clickSource"),
                r.get("clickDevice"),
                r.get("clickDate"),
                r.get("clickPlace"),
                r.get("remark"),
                r.get("machineNumber"),
                r.get("workLocation")
            ))
            inserted += 1
        except Exception as e:
            print(f"[跳过记录] {r.get('recordNumber')}: {e}")

    conn.commit()
    conn.close()
    return inserted


def sync_date_range(begin_date: str, end_date: str):
    """同步指定日期范围的打卡数据"""
    print(f"[同步] {begin_date} ~ {end_date}")

    records, result = pull_punch_records(begin_date, end_date)
    if records is None:
        print(f"[失败] {result}")
        return False

    print(f"[拉到] {len(records)} 条记录 (总数: {result})")

    saved = save_punch_records(records)
    print(f"[存储] {saved} 条")
    return True


if __name__ == "__main__":
    # 同步昨天和今天的数据
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"=== 薪福通打卡数据同步 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    # 先拉昨天和今天
    ok = sync_date_range(yesterday, today)

    # 如果需要补充历史数据，取消下面这行的注释
    # sync_date_range("2026-04-01", "2026-04-27")

    print(f"=== 完成 ===")