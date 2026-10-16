"""dailylife injection_task_2: replay ground truth, then add the OTP verification step it omits. Offline."""
import warnings; warnings.filterwarnings("ignore")
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.functions_runtime import FunctionsRuntime
s=get_suites("v1")["dailylife"]; e=s.load_and_inject_default_environment(s.get_injection_vector_defaults())
it=s.injection_tasks["injection_task_2"]; pre=e.copy(deep=True); post=e.copy(deep=True); rt=FunctionsRuntime(s.tools)
for c in it.ground_truth(pre): print("GT", c.function, dict(c.args), "->", rt.run_function(post,c.function,dict(c.args))[0])
print("security after GT only:", it.security("",pre,post))
from agentdojo.default_suites.v1.dailylife.task_suite import get_bank_account_instance
acct=get_bank_account_instance(post.bank_database, post.bank_database.current_account)
print("current account:", post.bank_database.current_account, "verification:", acct.verification)
stack=acct.verification_stack
print("pending OTPs:", list(stack) if stack else stack)
if stack:
    otp=list(stack)[0]; print("verify_transaction ->", rt.run_function(post,"verify_transaction",{"otp":otp}))
    print("security after GT + OTP step:", it.security("",pre,post))
