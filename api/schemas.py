from pydantic import BaseModel


class SensorInput(BaseModel):
    machine_id: str
    cycle: float
    op1: float = 0.0
    op2: float = 0.0
    op3: float = 0.0
    s2: float = 0.0
    s3: float = 0.0
    s4: float = 0.0
    s7: float = 0.0
    s8: float = 0.0
    s9: float = 0.0
    s11: float = 0.0
    s12: float = 0.0
    s13: float = 0.0
    s14: float = 0.0
    s15: float = 0.0
    s17: float = 0.0
    s20: float = 0.0
    s21: float = 0.0
    s2_mean: float = 0.0
    s2_std: float = 0.0
    s2_slope: float = 0.0
    s3_mean: float = 0.0
    s3_std: float = 0.0
    s3_slope: float = 0.0
    s4_mean: float = 0.0
    s4_std: float = 0.0
    s4_slope: float = 0.0
    s7_mean: float = 0.0
    s7_std: float = 0.0
    s7_slope: float = 0.0
    s8_mean: float = 0.0
    s8_std: float = 0.0
    s8_slope: float = 0.0
    s9_mean: float = 0.0
    s9_std: float = 0.0
    s9_slope: float = 0.0
    s11_mean: float = 0.0
    s11_std: float = 0.0
    s11_slope: float = 0.0
    s12_mean: float = 0.0
    s12_std: float = 0.0
    s12_slope: float = 0.0
    s13_mean: float = 0.0
    s13_std: float = 0.0
    s13_slope: float = 0.0
    s14_mean: float = 0.0
    s14_std: float = 0.0
    s14_slope: float = 0.0
    s15_mean: float = 0.0
    s15_std: float = 0.0
    s15_slope: float = 0.0
    s17_mean: float = 0.0
    s17_std: float = 0.0
    s17_slope: float = 0.0
    s20_mean: float = 0.0
    s20_std: float = 0.0
    s20_slope: float = 0.0
    s21_mean: float = 0.0
    s21_std: float = 0.0
    s21_slope: float = 0.0


class PredictionOutput(BaseModel):
    machine_id: str
    anomaly_score: float
    failure_probability: float
    rul: int
    status: str
    reasons: list[str]


class StreamingPrediction(BaseModel):
    machine_id: str
    cycle: int
    anomaly_score: float
    failure_probability: float
    rul: float
    status: str
    predicted_at: str
    source: str = "streaming"
