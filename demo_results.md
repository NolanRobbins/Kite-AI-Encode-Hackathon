What’s working
All 5 stages print: identity → reputation → negotiation → settlement → attestation.
demo.py is exercising real negotiatorgrid modules (opponent model, Nash guardrail, offer generator, attestation pipeline).
ASCII convergence chart renders; deal hash + KiteScan URL show up.
Runtime is ~6.7s — well within a live demo budget.
Problems to take seriously
1. Reputation wiring looks inverted (biggest novelty risk)
DataBuyer-Alpha  ★★★★☆  (4.8/5.0)
WeatherPro-Service  ★★★★☆  (4.5/5.0)
→ Buyer reputation 4.8/5.0 → strategy: cooperative
→ Seller reputation 4.5/5.0 → strategy: cooperative
Your README / critique doc sells “reputation‑conditioned strategy” as novel contribution #2: the buyer’s behavior changes based on the seller’s on-chain reputation. Here the buyer’s strategy is being derived from its own reputation, and the seller’s from its own. That is not the claim. Expected behavior: one line like “Seller reputation 4.5/5 → buyer strategy: cooperative” (and in Act 3, the dashboard script specifically wants a low-rep seller to flip the buyer to aggressive).

2. Opponent model is frozen
Every round prints:

Opponent model: est. reservation: $0.0985 (conf: 88%)
Six rounds in a row, identical. The README claims “linear regression on concession patterns estimates counterparty reservation prices in real time.” If the estimate and confidence never move after new offers arrive, the demo contradicts its own pitch. Either the update hook isn’t being called, or we’re reading a cached value.

3. LLM offer text is duplicated
Rounds 1–2, 3–4, and 5–6 have identical buyer lines (and identical seller lines). That reads like a deterministic template, not “GPT‑4o‑mini generates human‑readable offer explanations with context-aware persuasion arguments.” For a recorded video this will jump out — judges will assume no LLM is in the loop.

4. Deal price doesn’t match any offer in the visible transcript
Round 6 offers are buyer $0.0927 and seller $0.1073. The agreed price is $0.1034, which is:

not either agent’s offer,
not the midpoint ($0.1000),
not obviously derivable from the shown rounds.
Either a round 7 is happening silently, or NegMAS/NegotiationSession is picking a price without printing the acceptance. For a demo narrative (“two agents negotiated it”), you need a visible seller accepts buyer’s $0.X or symmetric moment, not a mystery number.

5. Nash check says PASS from round 1
Round 1 has buyer $0.08 vs seller $0.12 — a 50% gap. Labeling that “Nash check: PASS” right next to the round offers implies those offers are inside the Nash band, which is almost certainly not what NashGuardrail is actually computing. Most likely the guardrail only validates the agreed price and this label is being printed per-round regardless. That’s a misleading log that a game-theory judge will call out.

6. Settlement is mock — and says so on screen
Facilitator verify rejected: unknown; using mock
✓ Settlement confirmed!
This is fine for a dry run, but for the judged video you do not want “using mock” visible unless you own it in narration. Either:

fund the wallet + set the live facilitator env and get a real verify, or
suppress that line and make the log say Using mock facilitator (testnet offline) so it matches your honest claim.
Per NEXT_UP.md §2 and current_tech_problems.md, stablecoin/facilitator mismatches are a known issue — plan accordingly.

7. Utilities look low for a “fair” deal
Buyer utility 0.237, Seller utility 0.334, Global welfare 0.286. Fine numerically, but the pitch is Nash/fair bargaining — a welfare of 0.29 out of 1.0 invites the question “why is 71% of the surplus lost?”. Worth checking whether NegotiationSession is computing these against the correct reservation prices and normalization.

8. Missing demo acts (critical versus judge criteria)
Your own 8.3-negotiatorgrid-demo-script.md and negotiatorgrid-judge-critique.md say the autonomy / novelty points live in:

Act 3: MCP discovery of an unknown agent → reputation-conditioned strategy flip → ~30% cheaper deal.
Act 5: malicious seller → hash mismatch → payment refused → reputation penalty.
Neither act is exercised by demo.py in classic mode. Minimum to close the gap:

python demo.py --mode discovery
and a second invocation (or separate script) that runs executors/malicious_seller.py → triggers the hash-mismatch path. You already have tests/test_act3_compare.py, tests/test_act5_malicious.py, negotiatorgrid/executors/malicious_seller.py, and discovery/ — plumb them into demo.py or a second entrypoint so the CLI proves the two “wow moments,” not just the golden path.

What to fix before recording
Ranked by impact vs. effort:

Fix the reputation mapping so the buyer’s strategy is a function of the seller’s reputation (and vice versa if relevant). Log it as Seller reputation X → buyer strategy: Y.
Make the opponent model actually update each round (even if it’s a one-liner fix to feed OpponentModeler.update() with the latest offer). The log must show a moving estimate / confidence.
De-duplicate LLM offer text — add round number, last opponent offer, or concession delta into the prompt/template so consecutive rounds don’t print identical strings.
Print acceptance explicitly in stage 3 (“Seller accepts buyer’s $0.X in round N”) and make the agreed price provably equal to one side’s last offer, or explain the tie-breaking rule inline.
Either drop the per-round Nash check: PASS line or replace it with a real inside/outside‑band check against _price_grid() output. Keeping the misleading version is worse than removing it.
Hide or own the “using mock” line in settlement; add a one-line state label (mode=mock / mode=testnet) so the demo’s honesty is structural, not accidental.
Add --mode malicious (or similar) to demo.py that triggers malicious_seller.py and prints the hash‑mismatch rejection. That single addition recovers Act 5 without needing the dashboard.
Run python demo.py --mode discovery and record both — that is the version that matches the README’s 6‑stage pipeline and the judge-targeted story.
Does this output align with the project requirements?
Partially. It proves the engine works (good). It does not yet demonstrate your two strongest claims:

Reputation-conditioned negotiation (wired backwards or to the wrong agent).
Hash‑mismatch / anti-collusion (not in this run at all).
And it shows two surface bugs (frozen opponent model, duplicated LLM text) that undermine the “AI agent” framing. These are all small-diff fixes relative to the code you already have — core/opponent_model.py, core/reputation.py, llm/offer_generator.py, and the demo’s stage 3 formatting.

If you want, the next concrete step is for me to open demo.py + core/reputation.py + core/opponent_model.py and pinpoint the exact lines behind problems 1, 2, and 3 so you can fix them as one short patch.