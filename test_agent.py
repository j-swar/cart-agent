"""Standalone test for CartTriageAgent."""
from cart_agent.agent import CartTriageAgent
from raise_agent_sdk.runner import run_standalone

result = run_standalone(
    CartTriageAgent,
    provider = "google",               # ← changed from "openai"
    api_key  = None,                   # uses GOOGLE_API_KEY env var
    service  = "cart-service",
    alert    = "CheckoutFailed",
    severity = "p2",
)

print("\nTools called:")
for t in result["tools_called"]:
    print(f"  • {t['tool']}({t['params']}) → {t['result']}")

print(f"\nSummary: {result['summary'] or '(no summary)'}")
