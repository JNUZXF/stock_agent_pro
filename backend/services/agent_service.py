# backend/services/agent_service.py
# Agent服务封装，管理Agent实例和会话

import os
from typing import Dict, Optional
import sys
import os
# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.agents.stock_agent import StockAnalysisAgent, generate_guest_user_id


class AgentService:
    """Agent服务管理器
    
    负责管理多个Agent实例，每个conversation_id对应一个Agent实例
    """
    
    def __init__(self):
        """初始化服务"""
        self.agents: Dict[str, StockAnalysisAgent] = {}
    
    def get_or_create_agent(
        self, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> StockAnalysisAgent:
        """
        获取或创建Agent实例
        
        Args:
            conversation_id: 会话ID，如果为None则创建新Agent
            user_id: 用户ID，如果为None则自动生成游客ID
            
        Returns:
            StockAnalysisAgent实例
        """
        # 如果没有提供user_id，生成游客ID
        if not user_id:
            user_id = generate_guest_user_id()
        
        # 如果提供了conversation_id，尝试获取现有Agent
        if conversation_id and conversation_id in self.agents:
            agent = self.agents[conversation_id]
            # 如果Agent的user_id不匹配，更新它（这种情况不应该发生，但为了安全起见）
            if agent.user_id != user_id:
                agent.user_id = user_id
            return agent
        
        # 创建新Agent（如果提供了conversation_id，则使用它；否则Agent会自动生成）
        agent = StockAnalysisAgent(conversation_id=conversation_id, user_id=user_id)
        self.agents[agent.conversation_id] = agent
        return agent
    
    def get_agent(self, conversation_id: str) -> Optional[StockAnalysisAgent]:
        """
        获取指定会话的Agent实例
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            Agent实例，如果不存在则返回None
        """
        return self.agents.get(conversation_id)
    
    def remove_agent(self, conversation_id: str) -> bool:
        """
        移除Agent实例（用于清理内存）
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            是否成功移除
        """
        if conversation_id in self.agents:
            del self.agents[conversation_id]
            return True
        return False


# 全局服务实例
agent_service = AgentService()

