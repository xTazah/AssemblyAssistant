from pydantic import BaseModel

class ConfidenceScores(BaseModel):
    Forward: float
    Backward: float 
    Other: float