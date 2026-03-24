from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ConversationMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class InsightQuery(BaseModel):
    question: str
    disease: Optional[str] = None
    region: Optional[str] = None
    regions: Optional[List[str]] = None  # For multi-region comparison
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    conversation_history: Optional[List[ConversationMessage]] = None

class Correlation(BaseModel):
    factor1: str
    factor2: str
    correlation_coefficient: float
    p_value: float
    interpretation: str

class Anomaly(BaseModel):
    date: str
    value: int
    type: str  # 'spike' or 'drop'
    severity: str  # 'high' or 'medium'
    z_score: float
    deviation_pct: float

class InsightResponse(BaseModel):
    query: str
    narrative: str
    correlations: List[Correlation] = []
    supporting_data: Dict[str, Any] = {}
    visualization_data: Optional[Dict[str, Any]] = None
    anomalies: List[Anomaly] = []
    trend_data: Optional[Dict[str, Any]] = None
    caveats: List[str] = [
        "Correlation does not imply causation.",
        "These insights are hypotheses, not medical advice.",
        "Results are based on available data and may have limitations."
    ]
