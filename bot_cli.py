#!/usr/bin/env python3
import sys
from pathlib import Path
from bot_server import CodeJudgeBot, CONFIG

def judge_file(filepath: str):
    bot = CodeJudgeBot(CONFIG)
    
    with open(filepath, 'r') as f:
        code = f.read()
    
    result = bot.judge_code(code, Path(filepath).stem)
    verdict = bot.format_verdict(result)
    print(verdict)

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "judge":
        print("Usage: python3 bot_cli.py judge <file.py>")
        return
    
    judge_file(sys.argv[2])

if __name__ == "__main__":
    main()
