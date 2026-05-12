# Hermes Agent 记忆归档

> 归档时间：2026-05-12
> 记忆条目：13条 | 使用率：2200/2200 chars (100%)

---

## 今日工作记录（2026-05-12）

### 小程序正式上线
- 个人主体注册小程序：AppID `wx2038c50a1e125535`（seashine-hr）
- 旧测试号 `wx5ebe736348bebe19`（baobei_1314ai）已废弃
- 代码上传 v1.0.0（94.8KB）
- 服务器域名配置：`https://seashinehr.ccwu.cc`
- 提交审核 → 因缺少测试账号被拒 → 补充后通过审核
- 已发布上线（备案审核中，通过后完全正常）

### 系统服务修复
- **根因**：Mac 重启后所有服务挂了
- 旧 launchd plist 指向废弃项目 `/Users/jiuhua/HR系统/extracted`，端口错误
- **修复**：
  - 修正 `com.hrSystem.server.plist`：指向新项目 + 端口 8001 + 正确 Python 路径
  - 新建 `com.hr.cloudflared.plist`：Cloudflare Tunnel 自启
  - 新建 `com.hr.vite.plist`：前端开发服务器 5173 自启
- **小程序 baseUrl 修复**：从局域网 IP `192.168.110.6:8001` 改为公网 `https://seashinehr.ccwu.cc`
- 清理了重复进程（4个 uvicorn + 4个 cloudflared 互相打架）

### 新问题：换 Mac 迁移
- 用户预计明天（5月13日）换新 Mac
- 迁移清单已更新：tar 项目 + 3个 plist → 新 Mac 解压 → pip install + npm install → launchctl load

---

## 记忆快照

### 主项目
`/Users/jiuhua/deepseek创建HR系统/`（uvicorn:8001+SQLite）。launchd自启：com.hrSystem.server+cloudflared+vite(:5173)。

### 小程序
正式 AppID=wx2038c50a1e125535（个人主体，seashine-hr），baseUrl=https://seashinehr.ccwu.cc/api。

### 部门归类
花名册部门平级，子部门从 position 字段提取关键词。制造部：成形→成形课、加工→加工课、烧结→烧结课、渗碳→热处理课等。品质保证部：全检/检查→品保课，品质/QA→品管课。

### ZK同步
调 `/scripts/zk_sync_worker.py`，120s超时。xFace100三台。16人待导入。NAS RS818+。

### 班次规则
E班7:50-17:00、A班7:50-20:00、C班19:50-08:00。判定三层：scope定E → 8点规则 → 历史修正。换班判定待实现。

### 薪资规则
工龄工资（1年+50…封顶200）+ 学历工资（初中0/高中100/中专100/大专300/本科500/硕士800）。

### 待办
换班判定C↔A代码未实现、适用范围确认5/9、16名新员工待导入ZK。

### 账号
20150198陈敏(人事经理)/20170199徐妍(部门主管)/20220940王寅(HR专员)，密码hc@123。

### Mac迁移（预计2026-05-13）
tar .hermes+项目+3个plist → 新Mac解压 → pip/npm install → launchctl load → 启动。hr_v2.db 必搬。
