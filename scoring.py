from datetime import datetime, timedelta
from typing import Dict, Optional

class AppScorer:
    """为应用程序计算'坟墓分数'的类"""
    
    def __init__(self, weight_size: float = 2.0, weight_days: float = 0.01):
        self.weight_size = weight_size
        self.weight_days = weight_days
    
    def calculate_score(self, app: Dict) -> Dict:
        """计算应用的坟墓分数并确定状态"""
        size_gb = app.get('size', 0) / (1024 ** 3)  # 转换为GB
        days_since_last_use = self._calculate_days_since_last_use(app)
        
        # 计算分数
        score = self.weight_size * size_gb + self.weight_days * days_since_last_use
        
        # 确定状态
        status = self._determine_status(score, size_gb, days_since_last_use)
        
        return {
            'score': score,
            'size_gb': size_gb,
            'days_since_last_use': days_since_last_use,
            'status': status
        }
    
    def _calculate_days_since_last_use(self, app: Dict) -> int:
        """计算距离上次使用多少天"""
        last_access = app.get('last_access_time')
        if not last_access:
            # 如果没有访问时间，假设很久没用（比如1年）
            return 365
        
        if isinstance(last_access, datetime):
            delta = datetime.now() - last_access
            return max(0, delta.days)
        else:
            # 如果是字符串格式的时间
            try:
                last_dt = datetime.fromisoformat(last_access)
                delta = datetime.now() - last_dt
                return max(0, delta.days)
            except:
                return 365
    
    def _determine_status(self, score: float, size_gb: float, days: int) -> str:
        """根据分数和参数确定状态"""
        # 绿色：大文件且很久没用
        if size_gb > 1.0 and days > 90:
            return "🟢 安全卸载"
        # 红色：小文件或最近使用过
        elif size_gb < 0.1 or days < 30:
            return "🔴 可能仍需要"
        # 黄色：中等情况
        else:
            return "🟡 可考虑"