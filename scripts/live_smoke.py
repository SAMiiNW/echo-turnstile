import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result["method"] = method
    if args:
        result["args"] = args
    if kwargs:
        result["kwargs"] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
KEY = re.search(r'^ACCOUNT_1_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
client = create_client(chain=studionet, account=create_account(account_private_key=KEY))
address = json.loads((ROOT / "deployment.json").read_text(encoding="utf-8"))["contractAddress"]


def finalized(name, args, expected="SUCCESS"):
    tx = client.write_contract(address=address, function_name=name, args=args)
    print(name + "_tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(transaction_hash=tx, wait_until="finalized", retries=180, interval=5000, full_transaction=True)
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    assert receipt.get("result_name") == "MAJORITY_AGREE" and leader.get("execution_result") == expected, receipt
    return str(tx), leader


stamp = str(int(time.time()))
lane_id = "LANE-" + stamp
ticket_a = "REQ-A-" + stamp
ticket_b = "REQ-B-" + stamp
ticket_c = "REQ-C-" + stamp
rule = "Treat two requests as duplicates only when they ask for the same concrete deliverable for the same product area, even if wording or language differs. Shared topic alone is not enough."
base = "https://cdn.jsdelivr.net/gh/SAMiiNW/echo-turnstile@main/fixtures/"

open_tx, _ = finalized("open_lane", [lane_id, "Public product request intake", rule, 86400])
a_tx, _ = finalized("submit_ticket", [ticket_a, lane_id, "French settings localization", base + "request-a.md"])
b_tx, _ = finalized("submit_ticket", [ticket_b, lane_id, "Localize settings into French", base + "request-b.md"])
c_tx, _ = finalized("submit_ticket", [ticket_c, lane_id, "CSV preview before export", base + "request-c.md"])
a = client.read_contract(address=address, function_name="get_ticket", args=[ticket_a])
b = client.read_contract(address=address, function_name="get_ticket", args=[ticket_b])
c = client.read_contract(address=address, function_name="get_ticket", args=[ticket_c])
assert a["state"] == "ADMITTED" and not a["duplicate_ids"], a
assert b["state"] == "REDIRECTED" and ticket_a in b["duplicate_ids"], b
assert c["state"] == "ADMITTED" and not c["duplicate_ids"], c
before = client.read_contract(address=address, function_name="get_lane", args=[lane_id])
duplicate_tx, duplicate_leader = finalized("submit_ticket", [ticket_a, lane_id, "Duplicate identifier", base + "request-c.md"], expected="ERROR")
after = client.read_contract(address=address, function_name="get_lane", args=[lane_id])
assert before == after
proof = {
    "laneId": lane_id,
    "transactions": {"openLane": open_tx, "firstAdmission": a_tx, "semanticRedirect": b_tx, "distinctAdmission": c_tx, "duplicateIdRejected": duplicate_tx},
    "negativeExecution": duplicate_leader.get("execution_result"),
    "laneUnchangedAfterRejectedDuplicate": before == after,
    "tickets": {"first": a, "redirected": b, "distinct": c},
    "fixtureDisclosure": "The three public request pages are operator-controlled fixtures used to demonstrate admission, semantic redirect, and distinct admission.",
}
(ROOT / "evidence").mkdir(exist_ok=True)
(ROOT / "evidence" / "live-run.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
print(json.dumps(proof, indent=2), flush=True)
