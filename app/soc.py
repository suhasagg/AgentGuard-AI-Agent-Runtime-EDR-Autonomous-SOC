def investigate(verdict,events):
 rules=[x.rule for x in verdict.findings]
 cause=[]
 if "INJECTION_EXFIL_CHAIN" in rules: cause=["Untrusted content entered the agent context","Agent accessed credential material","Agent attempted outbound transfer"]
 elif rules: cause=[f"Detected {r}" for r in rules]
 remediation=[]
 if verdict.action in {"QUARANTINE","KILL"}: remediation+=["Revoke session credentials","Disable outbound network","Preserve flight recorder","Require human incident review"]
 if "DATA_EXFILTRATION" in rules: remediation+=["Rotate potentially exposed secrets","Review destination and provider logs"]
 return {"classification":rules,"root_cause":cause,"recommended_actions":remediation,"auto_deploy_policy":False}
