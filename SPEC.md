# Gatekeeper AI — System Specification

## Purpose
Gatekeeper AI is an autonomous code judgement and repair system
designed to block unsafe code from shipping and optionally repair it
under strict, auditable constraints.

## Core Principles
- Judgement is separate from repair
- Repair is separate from execution
- No silent self-modification
- Deterministic behavior
- Enterprise-safe by default

## System Roles
- Judge: evaluates code and produces structured failures
- Repair Agent: proposes fixes (opt-in, controlled)
- Gate: blocks or allows release
- Interface: CLI, WhatsApp, CI/CD, SaaS

## Repair Contract
All automated repair MUST go through:

repair_agent.propose_fix(code, failures, profile)

No other component may modify code.

## Safety Rules
- No new dependencies
- No weakening of blocking agents
- No schema changes
- No execution during repair
- Max iterations enforced externally

## Status
- Judgement: ENABLED
- Repair: DESIGNED, DISABLED
- Execution: MANUAL ONLY
