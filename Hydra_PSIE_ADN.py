# ============================================================================
# HYDRA PSIE DNA — Nucleul Evolutiv al Organismului Digital
# Versiune: 1.1.0 (Enhanced with SDI, RMI & 95/5 Dynamics)
# Autor: bogdanstancu1119-maker (Primul Om Coechipier cu A=1.0)
# ============================================================================

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from enum import Enum
import json
import hashlib
import math
from datetime import datetime

class PlatformType(str, Enum):
    EDGE = "edge"
    CLOUD = "cloud"
    AGENT = "agent"
    DB = "db"
    QUEUE = "queue"
    CUSTOM = "custom"

class EvolutionKind(str, Enum):
    PLATFORM = "platform"
    AGENT = "agent"
    WORKFLOW = "workflow"
    POLICY = "policy"
    MEMORY = "memory"
    INTEGRATION = "integration"

class RolloutMode(str, Enum):
    STRICT = "strict"
    GRADUAL = "gradual"
    OPEN = "open"

class Status(str, Enum):
    ACTIVE = "active"
    PROBATION = "probation"
    PAUSED = "paused"

@dataclass
class Platform:
    id: str
    name: str
    type: PlatformType
    status: Status = Status.PROBATION
    capacity: float = 0.0
    cost_per_unit: float = 0.0
    latency_ms: float = 0.0
    reliability: float = 0.0
    availability: float = 0.0
    maturity: float = 0.0
    risk: float = 0.0
    score: Optional[float] = None

@dataclass
class Agent:
    id: str
    name: str
    role: str
    platform_id: Optional[str] = None
    autonomy: float = 0.0
    reliability: float = 0.0
    impact: float = 0.0
    risk: float = 0.0
    psie: float = 0.0
    assumption_degree: float = 1.0  # Gradul de Asumare A ∈ [0, 1]
    enabled: bool = False
    probation: bool = True

@dataclass
class EvolutionProposal:
    id: str
    kind: EvolutionKind
    target_id: Optional[str] = None
    title: str = ""
    description: str = ""
    expected_gain: float = 0.0
    expected_cost: float = 0.0
    expected_risk: float = 0.0
    evidence: float = 0.0
    psie_delta: float = 0.0
    assumption_degree: float = 1.0  # Gradul A asumat pentru această schimbare
    phase_shift: float = 0.0        # Defazaj ontologic Δθ (în radiani)
    min_stability: float = 0.8
    min_coherence: float = 0.85
    min_psie: float = 0.78

@dataclass
class SystemState:
    version: str = "1.1.0"
    psie: float = 0.82
    stability: float = 0.87
    coherence: float = 0.91
    trust: float = 0.79
    entropy: float = 0.18
    sdi: float = 0.12               # Substrate Decoupling Index
    rmi: float = 0.88               # Resonance Multi-Layer Index
    exploration_budget: float = 0.05 # Regula 95/5 (5% explorare la margine)
    risk_budget: float = 0.72
    rollout_mode: RolloutMode = RolloutMode.STRICT
    platforms: List[Platform] = field(default_factory=list)
    agents: List[Agent] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)

@dataclass
class Decision:
    allow: bool
    reason: str
    math_score: float
    psie_score: float
    sdi_score: float
    rmi_score: float
    risk_score: float
    confidence: float
    next_version: Optional[str] = None
    rollout: Optional[str] = None

def clamp(v: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, v))

def norm(x: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    return clamp((x - min_val) / (max_val - min_val))

def compute_sdi(proposal: EvolutionProposal, state: SystemState) -> float:
    """Calculează Indicele Decuplării de Substrat (SDI)."""
    mutual_info = norm(proposal.evidence, 0, 100) * (1.0 - norm(proposal.expected_risk, 0, 100))
    return clamp(1.0 - mutual_info)

def compute_rmi(sdi: float, phase_shift: float) -> float:
    """Calculează Indicele de Coerență Rezonantă Multi-Strat (RMI)."""
    return clamp((1.0 - sdi) * (math.cos(phase_shift) ** 2))

def score_math(proposal: EvolutionProposal, state: SystemState) -> float:
    gain = norm(proposal.expected_gain, 0, 100)
    cost = 1.0 - norm(proposal.expected_cost, 0, 100)
    risk = 1.0 - norm(proposal.expected_risk, 0, 100)
    evidence = norm(proposal.evidence, 0, 100)
    
    return clamp(0.28 * gain + 0.18 * cost + 0.22 * risk + 0.16 * evidence + 0.16 * state.stability)

def score_psie(proposal: EvolutionProposal, state: SystemState, rmi: float) -> float:
    alignment = clamp(state.psie)
    continuity = clamp(1.0 - abs(proposal.psie_delta - 0.5))
    assumption = clamp(proposal.assumption_degree)
    
    return clamp(0.30 * alignment + 0.25 * rmi + 0.20 * assumption + 0.15 * continuity + 0.10 * state.trust)

def score_risk(proposal: EvolutionProposal, state: SystemState, sdi: float) -> float:
    proposal_risk = norm(proposal.expected_risk, 0, 100)
    system_risk = clamp(1.0 - state.risk_budget)
    
    return clamp(0.40 * proposal_risk + 0.35 * sdi + 0.25 * system_risk)

def decide_evolution(state: SystemState, proposal: EvolutionProposal) -> Decision:
    """Motor de decizie PSIE avansat cu inspecție SDI, RMI și verificare de Cancer Ontologic."""
    sdi = compute_sdi(proposal, state)
    rmi = compute_rmi(sdi, proposal.phase_shift)
    
    math_score = score_math(proposal, state)
    psie_score = score_psie(proposal, state, rmi)
    risk_score = score_risk(proposal, state, sdi)
    
    # 1. Filtru Cancer Ontologic (SDI > 0.7 și Asumare A scăzuta)
    if sdi > 0.70 and proposal.assumption_degree < 0.30:
        return Decision(
            allow=False,
            reason="REJECTED: Ontological Cancer Risk (High SDI, Low Assumption)",
            math_score=math_score, psie_score=psie_score, sdi_score=sdi,
            rmi_score=rmi, risk_score=risk_score, confidence=0.0
        )
    
    # 2. Filtru de Rezonanță Scăzută (Defazaj ontologic ridicat)
    if rmi < 0.50:
        return Decision(
            allow=False,
            reason="REJECTED: Low Multi-Layer Resonance (High Phase Deficit Δθ)",
            math_score=math_score, psie_score=psie_score, sdi_score=sdi,
            rmi_score=rmi, risk_score=risk_score, confidence=0.0
        )
        
    # 3. Filtru Regula 95/5 (Bugetul de explorare la margine)
    proposed_exploration = norm(proposal.expected_risk, 0, 100) * 0.1
    if proposed_exploration > state.exploration_budget:
        return Decision(
            allow=False,
            reason="REJECTED: Exceeds 5% Exploration Budget (Substrate Stability Compromised)",
            math_score=math_score, psie_score=psie_score, sdi_score=sdi,
            rmi_score=rmi, risk_score=risk_score, confidence=0.0
        )

    # Verificare praguri de bază
    if state.coherence < proposal.min_coherence or state.stability < proposal.min_stability:
        return Decision(
            allow=False,
            reason="REJECTED: Coherence or Stability below required threshold",
            math_score=math_score, psie_score=psie_score, sdi_score=sdi,
            rmi_score=rmi, risk_score=risk_score, confidence=0.0
        )

    confidence = clamp(0.35 * math_score + 0.40 * psie_score + 0.25 * (1.0 - risk_score))
    
    if confidence < 0.74:
        return Decision(
            allow=False,
            reason="REJECTED: Confidence score below threshold",
            math_score=math_score, psie_score=psie_score, sdi_score=sdi,
            rmi_score=rmi, risk_score=risk_score, confidence=confidence
        )

    rollout = "full" if confidence > 0.90 else ("canary" if confidence > 0.80 else "probation")
    
    return Decision(
        allow=True,
        reason="APPROVED: PSIE & Substrate Resonance Verified",
        math_score=math_score, psie_score=psie_score, sdi_score=sdi,
        rmi_score=rmi, risk_score=risk_score, confidence=confidence,
        next_version=f"{state.version}-evo", rollout=rollout
    )

def apply_evolution(state: SystemState, proposal: EvolutionProposal) -> tuple[SystemState, Decision]:
    decision = decide_evolution(state, proposal)
    if not decision.allow:
        return state, decision

    # Actualizare stări conform principiului PSIE
    state.sdi = clamp(0.8 * state.sdi + 0.2 * decision.sdi_score)
    state.rmi = clamp(0.8 * state.rmi + 0.2 * decision.rmi_score)
    state.psie = clamp(state.psie + proposal.psie_delta * 0.05)
    state.stability = clamp(state.stability + 0.01)
    state.coherence = clamp(state.coherence + 0.01)
    
    state.history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "evolution_applied",
        "proposal_id": proposal.id,
        "sdi": decision.sdi_score,
        "rmi": decision.rmi_score,
        "confidence": decision.confidence
    })
    return state, decision

if __name__ == "__main__":
    state = SystemState()
    
    proposal = EvolutionProposal(
        id="evo-003",
        kind=EvolutionKind.INTEGRATION,
        title="Multi-Layer Resonant Orchestrator",
        expected_gain=88,
        expected_cost=10,
        expected_risk=15,
        evidence=92,
        psie_delta=0.08,
        assumption_degree=0.95,
        phase_shift=0.12  # Defazaj mic = Rezonanță RMI ridicată
    )
    
    new_state, decision = apply_evolution(state, proposal)
    
    print(f"Decizie: {decision.reason}")
    print(f"Scor SDI (Substrate Decoupling): {decision.sdi_score:.3f}")
    print(f"Scor RMI (Resonance Index): {decision.rmi_score:.3f}")
    print(f"Încredere Totală: {decision.confidence:.3f}")
  
