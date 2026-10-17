import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
KEY = re.search(r'^ACCOUNT_1_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
client = create_client(chain=studionet, account=create_account(account_private_key=KEY))
code = (ROOT / "contracts" / "contract.py").read_text(encoding="utf-8")
transaction = os.environ.get("DEPLOYMENT_TX") or client.deploy_contract(code=code, args=[])
print("deploy_tx=" + str(transaction), flush=True)
receipt = client.wait_for_transaction_receipt(transaction_hash=transaction, wait_until="finalized", retries=180, interval=5000, full_transaction=True)
leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
address = receipt.get("data", {}).get("contract_address") or receipt.get("to_address")
assert receipt.get("result_name") == "MAJORITY_AGREE" and leader.get("execution_result") == "SUCCESS", receipt
result = {
    "network": "StudioNet",
    "account": "SAMiiNW",
    "contractAddress": address,
    "deploymentTransaction": str(transaction),
    "deploymentConsensus": receipt.get("result_name"),
    "deploymentExecution": leader.get("execution_result"),
    "sourceSha256": hashlib.sha256(code.encode()).hexdigest(),
    "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "repository": "https://github.com/SAMiiNW/echo-turnstile",
}
(ROOT / "deployment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2), flush=True)
