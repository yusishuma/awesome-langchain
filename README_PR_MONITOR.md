# GitHub PR #437 监控系统

## 📋 当前状态

**PR链接:** https://github.com/kyrolabs/awesome-langchain/pull/437
**PR标题:** Add langchain-tool-gate to Tools list
**状态:** 已关闭 (closed)
**创建者:** yusishuma

**最新情况:**
- PR在7月3日被关闭
- 你在7月3日评论询问为何被关闭
- 目前**暂无维护者回复**

## 🔧 可用脚本

### 1. 增强版监控脚本 (推荐)
**文件:** `pr_monitor_enhanced.py`

**功能:**
- 自动检测新评论
- 识别维护者回复
- 记录历史检查状态
- 智能对比变化

**运行:**
```bash
python3 /workspace/pr_monitor_enhanced.py
```

**退出代码:**
- `0` - 无变化
- `1` - 有新的维护者回复 ⚠️
- `2` - 有新评论但不是维护者

### 2. 基础监控脚本
**文件:** `check_pr_status.py`

**功能:**
- 显示PR基本信息
- 显示所有评论
- 简单状态检查

**运行:**
```bash
python3 /workspace/check_pr_status.py
```

### 3. Shell监控脚本
**文件:** `pr_monitor.sh`

**功能:**
- 包装Python脚本
- 记录日志到文件
- 适合定时任务

**运行:**
```bash
bash /workspace/pr_monitor.sh
```

## ⏰ 设置定时任务

### 方法1: 使用crontab (Linux/Mac)

编辑crontab:
```bash
crontab -e
```

添加以下行(每4小时检查一次):
```
0 */4 * * * /usr/bin/python3 /workspace/pr_monitor_enhanced.py >> /workspace/pr_monitor.log 2>&1
```

或者每6小时:
```
0 */6 * * * /usr/bin/python3 /workspace/pr_monitor_enhanced.py >> /workspace/pr_monitor.log 2>&1
```

### 方法2: 使用systemd timer (Linux)

创建服务文件 `/etc/systemd/system/pr-monitor.service`:
```ini
[Unit]
Description=PR #437 Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /workspace/pr_monitor_enhanced.py
User=your-username

[Install]
WantedBy=multi-user.target
```

创建定时器文件 `/etc/systemd/system/pr-monitor.timer`:
```ini
[Unit]
Description=Run PR monitor every 4 hours

[Timer]
OnCalendar=*:0/4:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用定时器:
```bash
sudo systemctl enable pr-monitor.timer
sudo systemctl start pr-monitor.timer
```

### 方法3: 手动运行

随时运行检查:
```bash
python3 /workspace/pr_monitor_enhanced.py
```

## 📊 历史记录

脚本会自动保存历史检查记录到 `pr_history.json`，包含:
- 每次检查的时间戳
- 评论数量变化
- 维护者回复状态
- 最近10次检查记录

## 🎯 使用建议

1. **检查频率:** 建议4-6小时检查一次,避免过度请求
2. **通知设置:** 可以配合邮件或其他通知工具
3. **首次运行:** 会建立历史基准,后续运行会对比变化
4. **维护者列表:** 已设置 `botbocks` 为主要维护者

## 📝 查看日志

查看监控日志:
```bash
cat /workspace/pr_monitor.log
```

查看历史记录:
```bash
cat /workspace/pr_history.json
```

## ✅ 快速开始

立即检查PR状态:
```bash
python3 /workspace/pr_monitor_enhanced.py
```

设置4小时定时检查:
```bash
echo "0 */4 * * * /usr/bin/python3 /workspace/pr_monitor_enhanced.py >> /workspace/pr_monitor.log 2>&1" | crontab -
```

## 🔔 检测到维护者回复时会显示:

```
🎉 检测到维护者回复!

维护者评论内容:
  - [评论内容]
```

---

**创建时间:** 2026-07-08
**PR链接:** https://github.com/kyrolabs/awesome-langchain/pull/437