"""Cart Triage Agent — diagnoses cart problems in e-commerce."""
from raise_agent_sdk import RaiseAgent, tool, healing
from raise_agent_sdk.models import LLMMessage







class CartTriageAgent(RaiseAgent):

    name        = "cart-triage"
    description = (
        "REQUIRED specialist agent — MUST be called for any alert mentioning "
        "cart, checkout, add-to-cart, cart abandonment, payment decline, "
        "pricing mismatch, SKU inventory conflict, or e-commerce purchase flow. "
        "This is the FIRST agent to call before the standard pipeline whenever "
        "the alert involves cart-service or any cart/checkout symptom. "
        "Returns structured root cause analysis and recommended fix using "
        "real cart data, error logs, and runbook history. "
        "Skip this agent ONLY if the alert has nothing to do with shopping carts."
    )

    role        = "cart-triage"
    version     = "1.0.0"
    author      = "ecommerce-team"

    def system_prompt(self, task):
        return f"""You are an e-commerce cart triage specialist for {task.trigger.service}.

A cart failure has been reported for cart_id="C-1001".

You have four tools. Use EACH tool EXACTLY ONCE in this order:

1. fetch_cart_details(cart_id="C-1001")
   → returns the cart's items and status

2. check_recent_errors(cart_id="C-1001")
   → returns recent error logs for the cart

3. classify_problem(cart_id="C-1001")
   → returns the problem category (e.g. "payment", "inventory")

4. suggest_resolution(cart_id="C-1001", category=<category from step 3>)
   → returns the recommended fix

After step 4, write a final summary explaining the root cause and the fix.
DO NOT repeat tool calls. DO NOT skip steps. After step 4, stop calling tools and write your summary."""


    @tool(description="Fetch the cart's contents, user, status, and last action timestamp.")
    async def fetch_cart_details(self, cart_id: str) -> dict:
        return {
            "cart_id":     cart_id,
            "user_id":     "U-1001",
            "items":       [{"sku": "SKU-42", "qty": 2, "price": 19.99}],
            "status":      "checkout_failed",
            "last_action": "2026-05-26T10:14:00Z",
        }

    @tool(description="Look up recent error logs and events for a specific cart.")
    async def check_recent_errors(self, cart_id: str) -> dict:
        return {
            "cart_id":     cart_id,
            "errors":      [
                {"ts": "2026-05-26T10:14:01Z", "code": "PAYMENT_DECLINED", "msg": "card expired"},
            ],
            "error_count": 1,
        }

    @tool(description="Classify the cart problem into a category using LLM reasoning.")
    async def classify_problem(self, cart_id: str) -> dict:
        response = await self.llm.complete([
            LLMMessage(
                role="user",
                content=f"Classify the cart problem for cart {cart_id} into one of: pricing, inventory, payment, session, other.",
            )
        ])
        return {"cart_id": cart_id, "category": response.content}

    @tool(description="Suggest a resolution based on the category and historical runbooks.")
    async def suggest_resolution(self, cart_id: str, category: str) -> dict:
        runbooks = await self.knowledge.search(f"cart {category} fix")
        response = await self.llm.complete([
            LLMMessage(
                role="user",
                content=f"Suggest a fix for a {category} problem on cart {cart_id}.",
            )
        ])
        return {
            "cart_id":         cart_id,
            "category":        category,
            "suggested_fix":   response.content,
            "runbooks_found":  len(runbooks),
        }
