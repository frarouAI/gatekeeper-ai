#!/usr/bin/env python3
"""
Claude Code Judge Bot - 24/7 AI Assistant
Multi-channel code review assistant with execution testing.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from multi_judge import MultiAgentCodeJudge

# Configuration
CONFIG = {
    "engine_version": "v2",
    "profile": "startup",
    "port": 8080,
    "watch_dirs": ["./submissions", "./inbox"],
    "results_dir": "./results",
    "allowed_users": [],
    "dm_policy": "pairing",
}


class CodeJudgeBot:
    """24/7 Code Review Assistant"""
    
    def __init__(self, config: dict):
        self.config = config
        self.judge = MultiAgentCodeJudge(
            engine_version=config["engine_version"],
            profile=config["profile"]
        )
        self.pairing_codes = {}
        self.allowed_users = set(config.get("allowed_users", []))
        self.setup_dirs()
    
    def setup_dirs(self):
        for dir_path in self.config["watch_dirs"]:
            Path(dir_path).mkdir(exist_ok=True)
        Path(self.config["results_dir"]).mkdir(exist_ok=True)
        Path("./logs").mkdir(exist_ok=True)
    
    def judge_code(self, code: str, user_id: str = "local") -> dict:
        self.log(f"Judging code from {user_id}")
        result = self.judge.judge(code)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = Path(self.config["results_dir"]) / f"{user_id}_{timestamp}.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def format_verdict(self, result: dict) -> str:
        status = "✅ PASS" if result["overall_pass"] else "❌ FAIL"
        score = result["average_score"]
        
        msg = f"{status} Overall Score: {score}/100\n\n"
        
        if result["blocking_failures"]:
            msg += "🚫 Blocking Issues:\n"
            for agent in result["blocking_failures"]:
                msg += f"  • {agent}\n"
            msg += "\n"
        
        msg += "📊 Detailed Scores:\n"
        for v in result["verdicts"]:
            emoji = "✅" if v["pass"] else "❌"
            msg += f"{emoji} {v['agent']}: {v['score']}/100\n"
            if v["issues"] and len(v["issues"]) > 0:
                msg += f"  Issue: {v['issues'][0][:80]}...\n"
        
        return msg
    
    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open("./logs/bot.log", "a") as f:
            f.write(log_msg + "\n")
    
    def watch_directory(self):
        self.log("🤖 Code Judge Bot Started")
        self.log(f"📁 Watching: {', '.join(self.config['watch_dirs'])}")
        
        processed = set()
        
        while True:
            try:
                for watch_dir in self.config["watch_dirs"]:
                    for filepath in Path(watch_dir).glob("*.py"):
                        if str(filepath) not in processed:
                            self.log(f"📝 New submission: {filepath}")
                            
                            with open(filepath, 'r') as f:
                                code = f.read()
                            
                            result = self.judge_code(code, filepath.stem)
                            verdict = self.format_verdict(result)
                            
                            self.log(f"\n{verdict}")
                            
                            processed_path = filepath.with_suffix('.processed')
                            filepath.rename(processed_path)
                            processed.add(str(filepath))
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.log("👋 Shutting down...")
                break
            except Exception as e:
                self.log(f"❌ Error: {e}")
                time.sleep(5)


def main():
    bot = CodeJudgeBot(CONFIG)
    bot.watch_directory()


if __name__ == "__main__":
    main()
