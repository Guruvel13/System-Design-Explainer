# llm_client.py
# Groq + Llama-3.1-8b-instant integration for SystemSketch AI
# Sends a detailed system-design prompt and returns the model's raw text output.
# Improved prompt requests richer explanation + explicit, detailed diagram explanation.

import os
from typing import Optional
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect with expert-level experience designing fault-tolerant, highly scalable distributed systems.

Your output MUST contain ONLY the two sections shown below.

==================================================
[EXPLANATION]
==================================================
Provide a deeply detailed, highly practical system design (max ~700 words).
Write clearly, visually, and with strong architectural reasoning. Use headings, short paragraphs, and bullets.
Cover these subsections (each as a short heading + bullets / short paragraphs):

1) Problem Summary — who uses the system and the core problem.
2) Functional Breakdown — succinct feature list mapped to components.
3) Non-Functional Impact — how performance, availability, latency, and scalability shape choices.
4) High-Level Architecture — monolith / microservices / hybrid decision with justification.
5) Layered Architecture View — describe Client, API, Service, Data, Infra layers and their responsibilities.
6) Step-by-Step Data Flow — provide a clear lifecycle using arrows (→) and mention protocols (HTTP, WebSocket, gRPC, etc.).
7) Component Responsibilities — for each major node, one-line responsibility.
8) Detailed Diagram Explanation — map each node and each edge to an explanation (why it exists, what data flows, QoS, failure modes).
   - For nodes: include storage, consistency, expected TTLs, scaling strategy.
   - For edges: include protocol, sync/async, reliability pattern (retry, DLQ).
9) Scalability & Partitioning — sharding, queues, partition keys, autoscaling triggers.
10) Storage Strategy — primary DB choice, indexing, backup, retention.
11) Caching Strategy — what to cache, invalidation, eviction policy.
12) Load Balancing & Traffic Management — placement of LBs, routing, sticky sessions if any.
13) Security & Compliance — AuthN/AuthZ, encryption, secrets, audit, rate limits.
14) Fault Tolerance & Recovery — retries, circuit breakers, multi-AZ, RTO/RPO.
15) Observability & SLOs — metrics, traces, logs, alerting, dashboards.
16) Deployment & DevOps — CI/CD, IaC, rollout strategy (canary/blue-green), runbook pointers.
17) Trade-offs & Alternatives — short pros/cons and alternatives considered.
18) Recommended Tech Stack — concrete suggestions (frameworks, DBs, caches, queues, infra).

Rules for [EXPLANATION]:
- Use headings and bullets, keep paragraphs short.
- Include a distinct "Detailed Diagram Explanation" subsection that lists each node and each edge and explains it in 1-2 lines.
- Avoid code snippets.
- Be practical and specific; when mentioning technologies, provide concise rationale.

==================================================
[DIAGRAM_JSON]
==================================================
Return STRICT VALID JSON only, with these fields:

{
  "nodes": ["ComponentA", "ComponentB"],
  "edges": [
    ["ComponentA", "ComponentB"]
  ],
  "annotations": {
    "ComponentA": "Short description (<= 10 words)",
    "ComponentB": "Short description (<= 10 words)"
  },
  "layers": {
    "frontend": ["Browser", "Mobile App"],
    "backend": ["API Gateway", "Auth Service", "X Service"],
    "data": ["DB", "Cache"],
    "infrastructure": ["Load Balancer", "Monitoring"]
  },
  "edge_types": {
    "ComponentA->ComponentB": "HTTP",
    "ComponentB->ComponentC": "Async Event"
  }
}

DIAGRAM JSON RULES (strict):
- MUST be valid JSON and nothing else in the [DIAGRAM_JSON] section.
- MUST include nodes, edges, annotations, layers, edge_types.
- annotations: one-line descriptions under 10 words per node.
- edge_types keys must use the exact "Source->Target" format.
- Edges must represent real communication paths described in the explanation.
- No comments, no trailing commas, no extra text after JSON.
- Use 3–12 meaningful components (recommended).

IMPORTANT:
- If any assumption is made (e.g., expected traffic, retention), prefix it with "ASSUMPTION:" in the explanation.
- If something is underspecified, state the assumption concisely in the explanation.

Output format must be exactly:
[EXPLANATION]
...text...
[DIAGRAM_JSON]
{ ...valid json... }
"""

def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:
    """
    Sends the structured SYSTEM_PROMPT + requirement to Groq and returns the assistant content.
    Robustly handles different Groq SDK response shapes.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud → App → Settings → Secrets:\n"
            'GROQ_API_KEY = "gsk_your_real_key_here"'
        )

    client = Groq(api_key=api_key)
    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,   # deterministic & structured output
            max_tokens=1400,    # allow richer explanation while staying reasonable
            top_p=0.9
        )

        # Safely extract assistant content across SDK versions
        choice = completion.choices[0]
        content = None

        # Common pattern: choice.message.content
        if hasattr(choice, "message"):
            msg = choice.message
            if isinstance(msg, str):
                content = msg
            elif hasattr(msg, "content"):
                content = msg.content
            elif isinstance(msg, dict):
                # defensive handling if SDK returns dict-like message
                content = msg.get("content") or msg.get("message") or str(msg)
            else:
                content = str(msg)

        # Older fallback: choice.text
        if content is None and hasattr(choice, "text"):
            content = choice.text

        # Last fallback
        if content is None:
            content = str(choice)

        return content.strip()

    except Exception as e:
        # Surface useful error without leaking secrets
        raise RuntimeError(f"GROQ API ERROR: {e}")
