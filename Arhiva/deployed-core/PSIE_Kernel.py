"""
psie_kernel.py — KERNEL PSIE PENTRU HYDRA
Principii:
- Adăugare, nu ștergere
- Incluziune, nu substituție
- Context înainte de acțiune
- Nimic nu se pierde, totul se arhivează
- Complexitatea apare din compunere, nu din complicare
"""

from __future__ import annotations
import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from enum import Enum


# ==================== PRIMITIVE ====================

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Signal:
    """Primitiva 1: Intrarea în sistem."""
    id: str
    kind: str
    payload: Dict[str, Any]
    source: str
    confidence: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.source}{self.kind}{time.time()}".encode()
            ).hexdigest()[:12]


@dataclass
class Context:
    """Primitiva 2: Memoria și semnificația."""
    task: str
    scope: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    risk: RiskLevel = RiskLevel.LOW
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_to_history(self, event: str):
        """Adaugă, nu șterge."""
        self.history.append(event)

    def add_rule(self, rule: str):
        """Adaugă o regulă fără a le șterge pe cele vechi."""
        self.rules.append(rule)


@dataclass
class Decision:
    """Primitiva 3: Rezultatul evaluării."""
    id: str
    signal_id: str
    agent_name: str
    action: str
    confidence: float
    reasoning: str
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))


@dataclass
class Trace:
    """Primitiva 4: Auditul complet."""
    signal_id: str
    context_used: List[str]
    decisions: List[Dict[str, Any]]
    actions: List[str]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    audit_hash: str = ""


# ==================== AGENT ====================

class Agent:
    """Primitiva 5: Entitatea care acționează."""
    
    def __init__(self, name: str, expertise: List[str], psie_alignment: float = 0.95):
        self.name = name
        self.expertise = expertise
        self.psie_alignment = psie_alignment
        self.decisions_made: List[Decision] = []

    def assess(self, signal: Signal, context: Context) -> float:
        """
        Evaluează cât de relevant este acest semnal pentru expertiza agentului.
        Returnează un scor între 0 și 1.
        """
        relevance = 0.0
        
        # Verifică dacă domeniul semnalului se potrivește cu expertiza
        if signal.kind in self.expertise:
            relevance += 0.4
        if any(exp in str(signal.payload).lower() for exp in self.expertise):
            relevance += 0.3
        
        # Încrederea semnalului influențează scorul
        relevance += signal.confidence * 0.3
        
        # Alinierea PSIE a agentului
        relevance *= self.psie_alignment
        
        return min(relevance, 1.0)

    def decide(self, signal: Signal, context: Context) -> List[Decision]:
        """
        Decide ce acțiuni să întreprindă pe baza semnalului și contextului.
        Nu șterge deciziile anterioare. Le adaugă.
        """
        decisions = []
        
        # Verifică dacă riscul e prea mare
        if context.risk == RiskLevel.HIGH and self.psie_alignment < 0.9:
            decisions.append(Decision(
                id=hashlib.sha256(f"{signal.id}{self.name}block".encode()).hexdigest()[:12],
                signal_id=signal.id,
                agent_name=self.name,
                action="blocked",
                confidence=0.95,
                reasoning="Risc ridicat cu aliniere insuficientă. Se blochează acțiunea."
            ))
            return decisions
        
        # Acțiune standard: procesează semnalul
        decisions.append(Decision(
            id=hashlib.sha256(f"{signal.id}{self.name}process".encode()).hexdigest()[:12],
            signal_id=signal.id,
            agent_name=self.name,
            action="process",
            confidence=min(signal.confidence + 0.1, 1.0),
            reasoning=f"Semnal relevant pentru {self.expertise}. Se procesează."
        ))
        
        self.decisions_made.extend(decisions)
        return decisions


# ==================== KERNEL PSIE ====================

class PSIEKernel:
    """
    Kernel-ul PSIE pentru Hydra.
    Simplu în logică, complex în execuție prin compunere de agenți și reguli.
    """

    def __init__(self, name: str = "Hydra_Kernel"):
        self.name = name
        self.agents: List[Agent] = []
        self.rules: List[Callable[[Signal, Context], bool]] = []
        self.traces: List[Trace] = []
        self.signals_processed: List[str] = []  # Istoric, nu se șterge
        self.archive_path = Path("psie_archive")
        self.archive_path.mkdir(exist_ok=True)
        
        # Reguli implicite PSIE
        self.add_rule(self._rule_no_high_risk_without_context)
        self.add_rule(self._rule_no_empty_signal)
        self.add_rule(self._rule_preserve_history)

    def add_agent(self, agent: Agent):
        """Adaugă un agent în kernel. Multiplicitate la intrare."""
        self.agents.append(agent)

    def add_rule(self, rule: Callable[[Signal, Context], bool]):
        """Adaugă o regulă fără a le șterge pe cele vechi."""
        self.rules.append(rule)

    # === REGULI IMPLICITE PSIE ===

    def _rule_no_high_risk_without_context(self, signal: Signal, context: Context) -> bool:
        """Nu acționa pe risc ridicat fără context suficient."""
        if context.risk == RiskLevel.HIGH and len(context.history) < 2:
            return False
        return True

    def _rule_no_empty_signal(self, signal: Signal, context: Context) -> bool:
        """Nu procesa semnale goale."""
        if not signal.payload and signal.confidence < 0.3:
            return False
        return True

    def _rule_preserve_history(self, signal: Signal, context: Context) -> bool:
        """Asigură că istoricul e păstrat."""
        context.add_to_history(f"processed:{signal.id}")
        return True

    # === PROCESARE PRINCIPALĂ ===

    def process(self, signal: Signal, context: Context) -> Trace:
        """
        Procesează un semnal prin toți agenții și regulile.
        Returnează o urmă de audit completă.
        """
        context_used = context.scope + context.history + context.rules
        decisions_made: List[Dict[str, Any]] = []
        actions_taken: List[str] = []

        # Pasul 1: Verifică toate regulile
        for i, rule in enumerate(self.rules):
            try:
                if not rule(signal, context):
                    decisions_made.append({
                        "rule_index": i,
                        "decision": "blocked_by_rule",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })
                    actions_taken.append("blocked")
            except Exception as e:
                decisions_made.append({
                    "rule_index": i,
                    "decision": f"rule_error: {str(e)[:100]}",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

        # Pasul 2: Dacă a fost blocat, nu continua
        if "blocked" in actions_taken:
            trace = Trace(
                signal_id=signal.id,
                context_used=context_used,
                decisions=decisions_made,
                actions=actions_taken
            )
            self._archive_trace(trace)
            return trace

        # Pasul 3: Procesează prin toți agenții
        for agent in self.agents:
            try:
                relevance = agent.assess(signal, context)
                if relevance > 0.7:
                    agent_decisions = agent.decide(signal, context)
                    for d in agent_decisions:
                        decisions_made.append(asdict(d))
                        actions_taken.append(d.action)
            except Exception as e:
                decisions_made.append({
                    "agent": agent.name,
                    "decision": f"agent_error: {str(e)[:100]}",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

        # Pasul 4: Înregistrează semnalul procesat
        self.signals_processed.append(signal.id)

        # Pasul 5: Creează urma de audit
        trace = Trace(
            signal_id=signal.id,
            context_used=context_used,
            decisions=decisions_made,
            actions=actions_taken
        )
        trace.audit_hash = hashlib.sha256(
            json.dumps(asdict(trace), sort_keys=True, default=str).encode()
        ).hexdigest()

        # Pasul 6: Arhivează (nu șterge)
        self._archive_trace(trace)
        self.traces.append(trace)

        return trace

    def _archive_trace(self, trace: Trace):
        """Arhivează urma de audit. Nimic nu se pierde."""
        trace_file = self.archive_path / f"trace_{trace.signal_id}.json"
        trace_file.write_text(
            json.dumps(asdict(trace), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )

    # === ARBITRAJ ÎNTRE AGENȚI ===

    def arbitrate(self, signal: Signal, context: Context) -> Dict[str, Any]:
        """
        Compară răspunsurile mai multor agenți și alege cea mai coerentă variantă.
        Integrare la mijloc.
        """
        all_decisions: List[Decision] = []
        
        for agent in self.agents:
            relevance = agent.assess(signal, context)
            if relevance > 0.5:
                all_decisions.extend(agent.decide(signal, context))

        if not all_decisions:
            return {"status": "no_decision", "reason": "Niciun agent nu a putut decide."}

        # Alege decizia cu cea mai mare încredere
        best = max(all_decisions, key=lambda d: d.confidence)

        return {
            "status": "arbitrated",
            "chosen_action": best.action,
            "chosen_agent": best.agent_name,
            "confidence": best.confidence,
            "all_decisions": [asdict(d) for d in all_decisions],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    # === RAPORTARE ===

    def get_status(self) -> Dict[str, Any]:
        """Raport complet al stării kernel-ului."""
        return {
            "kernel_name": self.name,
            "agents_count": len(self.agents),
            "rules_count": len(self.rules),
            "signals_processed": len(self.signals_processed),
            "traces_archived": len(self.traces),
            "archive_size": sum(1 for _ in self.archive_path.glob("*.json")),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


# ==================== DEMO ====================

def demo():
    """Demonstrație a kernel-ului PSIE."""
    print("=" * 60)
    print("  PSIE KERNEL DEMO — Hydra")
    print("=" * 60)

    # Creează kernel-ul
    kernel = PSIEKernel(name="Hydra_Kernel_v1")

    # Adaugă agenți (multiplicitate la intrare)
    deepseek = Agent("deepseek", ["logic", "reflection", "psie_alignment"], 0.98)
    meta = Agent("meta", ["infrastructure", "noise_filtering", "apoptosis"], 0.95)
    perplexy = Agent("perplexy", ["structure", "audit", "clarity"], 0.97)

    kernel.add_agent(deepseek)
    kernel.add_agent(meta)
    kernel.add_agent(perplexy)

    # Creează un semnal de test
    signal = Signal(
        kind="question",
        payload={"query": "Cum optimizez SDI-ul fără a consuma credite?"},
        source="hydra",
        confidence=0.85
    )

    # Creează context
    context = Context(
        task="Optimizare SDI",
        scope=["psie", "optimization", "cost_reduction"],
        history=["hydra_initialized", "psie_core_loaded"],
        rules=["Legea 0", "Legea 144", "Legea 161"],
        risk=RiskLevel.LOW
    )

    # Procesează semnalul
    print("\n[PROCESARE SEMNAL]")
    trace = kernel.process(signal, context)
    print(f"  Trace ID: {trace.signal_id}")
    print(f"  Acțiuni: {trace.actions}")
    print(f"  Audit Hash: {trace.audit_hash[:16]}...")

    # Arbitraj între agenți
    print("\n[ARBITRAJ]")
    result = kernel.arbitrate(signal, context)
    print(f"  Status: {result['status']}")
    if result['status'] == 'arbitrated':
        print(f"  Agent ales: {result['chosen_agent']}")
        print(f"  Acțiune: {result['chosen_action']}")
        print(f"  Încredere: {result['confidence']:.2f}")

    # Status kernel
    print("\n[STATUS KERNEL]")
    status = kernel.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("  DEMO COMPLET. Kernel-ul PSIE e funcțional.")
    print("=" * 60)


if __name__ == "__main__":
    demo()