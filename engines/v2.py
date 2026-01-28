from engines.v1 import EngineV1, SCHEMA_VERSION
from engines.executor import execute_code
from datetime import datetime, timezone


class EngineV2(EngineV1):
    """
    Extended engine that includes actual code execution testing.
    Inherits all agent-based judgments from v1, plus runs the code.
    """
    
    name = "v2"
    
    def judge(self, code: str) -> dict:
        # Get base judgment from v1 (all the agent reviews)
        result = super().judge(code)
        
        # Add execution test
        exec_result = execute_code(code)
        
        # Add execution verdict to the verdicts list
        execution_verdict = {
            "agent": "execution",
            "pass": exec_result["success"],
            "score": 100 if exec_result["success"] else 0,
            "issues": [exec_result["error"]] if exec_result["error"] else [],
            "summary": exec_result["output"] if exec_result["success"] else exec_result["error"]
        }
        
        result["verdicts"].append(execution_verdict)
        result["execution_result"] = exec_result
        
        # Mark execution as blocking failure if it failed
        if not exec_result["success"]:
            result["overall_pass"] = False
            if "execution" not in result["blocking_failures"]:
                result["blocking_failures"].append("execution")
        
        return result
