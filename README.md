# diviora-orchestrator

A deterministic, auditable workflow engine for orchestrating AI-assisted work.

## Overview

`diviora-orchestrator` is not an autonomous agent.

It is a structured workflow runner that:
- accepts a goal and context
- generates a plan using an LLM
- executes steps using deterministic tools
- records all actions and outputs
- enforces strict guardrails and evaluation gates

This system is designed to eliminate back-and-forth prompting and replace it with repeatable, inspectable execution.

## Core Principles

- Agents decide, code executes
- All actions are traceable
- Fail closed by default
- No hidden side effects
- Deterministic outputs > clever behavior

## Architecture

### 1) Interface Layer (Input Surface)

Handles incoming requests via:
- CLI (primary)
- Optional adapters (web, chat, etc.)

Outputs:
- structured plan
- required approvals
- generated artifacts (docs, reports, code)

Invariant: Input is text. Output is structured artifacts.

### 2) State + Ledger (Single Source of Truth)

Persistent run state including:
- run_id
- goal
- context_refs
- plan (step-by-step)
- decisions (approved/rejected)
- executions (tool calls)
- artifacts
- errors

Implementation:
- SQLite (initial)
- File-based artifact storage: /artifacts/{run_id}/

Invariant: Every action is logged and reproducible.

### 3) Planner (LLM - Bounded Scope)

Generates a structured plan with step types:
- DECISION_REQUIRED
- DETERMINISTIC_EXECUTION
- HUMAN_TASK
- RESEARCH_READONLY

The planner does not execute anything.

Invariant: Planning only, no side effects.

### 4) Executor (Tool Runner)

Executes steps using predefined tools:
- file operations
- API calls
- test execution
- documentation generation
- browser automation (Playwright)
- repository interaction

Each execution logs:
- inputs
- outputs
- duration
- success/failure

Invariant: No execution without a planned step.

### 5) Policy + Guardrails

Enforces:
- allowed tools per workflow
- approval requirements
- scope constraints (repo, environment)
- secret handling rules

If ambiguity is detected, execution pauses.

Invariant: When in doubt, do not act.

### 6) Evaluation Gate (Quality Enforcement)

Defines completion criteria such as:
- tests passing
- evaluation scores meeting thresholds
- documentation completeness
- UI verification success

Workflow:
- execute → evaluate → if fail → generate fix tasks → repeat

Invariant: Outcomes must be measurable and verifiable.

## Workflow Packs

The system is designed around reusable workflow definitions.

### RAG Reliability Pack
- runs evaluation suite
- identifies failures
- proposes fixes (docs, chunking, retrieval)
- outputs improvement report

### UI Verification Pack
- converts claims into Playwright checks
- executes UI validation
- outputs verification report

### Research Pack
Used for structured investigation tasks such as:
- API integration strategies
- EDI parsing libraries
- UI framework options

Outputs:
- single markdown report per topic
- includes options, risks, and recommendation

## Tech Stack

Recommended baseline:
- Python
- SQLite
- Pydantic
- CLI (Typer or Click)
- Structured logging (JSON)

Optional:
- FastAPI (service mode)
- Playwright (UI validation)
- LangGraph (state orchestration)

## System Flow

User Goal
  ↓
Planner (LLM)
  ↓
Structured Plan
  ↓
Approval (if required)
  ↓
Executor (tools only)
  ↓
Artifacts + Logs
  ↓
Evaluation Gate
  ↓
PASS / FAIL

## Design Summary

diviora-orchestrator is a deterministic, auditable workflow runner that uses LLMs only for planning and drafting, while all execution is performed by explicit tools under strict guardrails and evaluated through repeatable quality gates.

## Status

Early-stage system focused on:
- reliability over autonomy
- auditability over speed
- structured execution over prompt iteration

## Future Work

- additional workflow packs
- richer UI adapters
- distributed execution
- automated retry loops (evaluation-driven)

## Why This Exists

Because prompt loops don’t scale.

This system replaces:
- manual iteration
- hidden reasoning
- inconsistent outputs

with:
- structured plans
- deterministic execution
- measurable results
