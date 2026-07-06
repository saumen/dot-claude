---
name: swordy-manage-llama-model
description: Add or edit llama.cpp server provider models from HuggingFace GGUF repos. Manages model configs across llama-server-launcher, .pi/agent, and .omp/agent. For vLLM model management, use /swordy-manage-vllm-model instead.
usage: /swordy-manage-llama-model <HF-URL | MODEL_NAME [adjust] field to value ...>
disable-model-invocation: true
---

# Add or Edit Model Configuration

**Scope:** This command manages **llama.cpp server provider models only** (GGUF variants launched via llama-server). It does NOT manage vLLM models — for those, use `/swordy-manage-vllm-model` when available.

**Boundary rules:**
- Only modifies `llama.ai-gateway.swordfish` / `llama@ai-gateway.swordfish` blocks across all repos
- Never touches `vllm.*` references in any file
- Works exclusively with GGUF quantization variants from HuggingFace
- Does NOT manage model inference, serving, or runtime behavior — only configuration and metadata


**Add mode**: Input is a HuggingFace model card URL or repo ID as `$1` (e.g., `https://huggingface.co/<org>/<repo>-GGUF`).

**Edit mode**: Input is a model alias + field keyword (e.g., `context`, `max tokens`, `cost`, `maxTokens`) — `adjust` is optional. Examples: `flash context window to 262144`, `flash adjust max tokens to 131072`, `flash increase context`.

## Path Aliases

Use these throughout — expand to full path before any edit:

| Alias | Full Path |
|---|---|
| `$LLM` | `/Users/swordfish/workspace/github/saumen/llama-server-launcher` |
| `$HF` | `/Users/swordfish/.cache/huggingface/hub` |
| `$PI` | `~/.pi/agent` |
| `$OMP` | `~/.omp/agent` |

## Mode Selection

Determine intent from the argument:
- **Edit mode first**: If the argument contains a model alias AND at least one field keyword (`context`, `max tokens`, `maxTokens`, `cost`, `reasoning`, `input`, `temperature`, `top-p`, `top-k`, `presence-penalty`, `frequency-penalty`, `ctx-size`), execute Phase 8 immediately and stop. Do NOT read Phases 1–7.
- **Add mode**: A HuggingFace URL or repo ID is provided → proceed to Phase 1.

## Phase 1: Fetch & Parse Metadata (Add Mode)

**Skip this phase in Edit mode.**

1. Fetch HF repo README and files.
2. Extract:
   - HuggingFace repo ID (e.g., `<org>/<repo>-GGUF`)
   - Available GGUF quantization variants (e.g., Q4_K_M, Q4_K_XL, Q5_K_M, Q5_K_XL, UD-Q4_K_XL, etc.)
   - Architecture type (Dense, MoE, LWM)
   - Context window (integer)
   - Reasoning capability (boolean)
   - Input types (["text"] or ["text", "image"])
   - mmproj presence (multimodal?)
   - MTP support (check for MTP drafter models or mention in README)
3. Identify model family for routing docs (e.g., `qwen3.6`, `gemma-4`, or **new family** like `ornith-1.0`).

## Phase 2: Quantization Variant Selection

1. If multiple GGUF quantization variants are available, **use the `ask_user_question` tool** to present the options to the user and let them select their preference.
   - Options should include the specific variants found (e.g., "Q4_K_M", "Q4_K_XL (UD)", "Q5_K_M", "Q5_K_XL (UD)").
   - Include a "Type something." or custom answer option if they want a specific variant not listed.
2. If only one variant is available or clearly recommended by the provider (e.g., Unsloth UD-Q4_K_XL for Gemma-4 QAT), confirm with the user or proceed with that variant.

## Phase 3: Validate & Assign Costs

- Validate: `maxTokens < contextWindow` (strict).
- Auto-assign costs based on architecture and selected variant:
  - MoE with ~3B active params (e.g., Qwen3.6-35B-A3B): `input=3, output=15, cacheRead=0.3, cacheWrite=3.75`
  - Dense 27B+ or MoE 26B+ (e.g., Gemma-4-26B-A4B, Qwen3.6-27B): `input=10, output=50, cacheRead=1.0, cacheWrite=12.5`
  - LWM models: `input=5, output=25, cacheRead=0.5, cacheWrite=6.25`

- Claude equivalent mapping for docs/models.md Cost Tracking table:
  - **flash** (NT/non-thinking): ≈ Haiku 4.5
  - **general** (thinking, general-purpose): ≈ Sonnet 4
  - **coder** (thinking, coding): ≈ Sonnet 4
  - **expert** (dense, high-stakes): ≈ Fable 5 / Opus 4.8
  - Use these labels in the "Claude Equivalent" column of the cost table.

## Phase 4: Handle New Model Family (If Applicable)

If the model family is **not** an existing one (qwen3.6, gemma-4, nex-mini, etc.):

1. **Create launcher directory**: `$LLM/launchers/<family>-mtp/` (or `<family>-gguf/` if no MTP support).
2. **Create catalog INI template**: `$LLM/launchers/<family>-mtp/<family>-catalog.ini` (or `<family>-mtp.ini`). Populate with base defaults and empty preset blocks to be filled in Phase 5.
3. **Create launcher bash script**: `$LLM/launcher-<family>.sh` in the root dir. Copy from existing template (`launcher-qwen.sh` or `launcher-gemma.sh`), adjust:
   - `preset='<family>-catalog'` or `<family>-mtp.ini` path
   - `--port <port>` — search all `$LLM/launcher-*.sh` for `--port` values, pick the next integer not in use (e.g., if 7080 and 8080 are taken, use 9080)
4. **Create docs dir and routing doc**: `$LLM/launchers/<family>-mtp/docs/<family>-model-routing.md` with initial structure (Executive Summary, Benchmarks table placeholder, Decision Matrix placeholder, Sources).

## Phase 5: Research Inference Parameters

**Before writing preset values, research the model card, blog, and official docs for model-specific inference recommendations.**

1. Search the HF model card for `temperature`, `top_p`, `top_k`, `presence_penalty`, `frequency_penalty`, or any sampling params in the quickstart/example sections.
2. Check the model author's blog/website for serving recipes or benchmark configurations.
3. Note which params are **officially recommended** vs **inherited from convention** vs **default/unknown**.
4. If the model uses a known chat template (e.g., `qwen3`, `llama3`), use that to determine `chat-template-kwargs` and `reasoning` settings.

## Phase 6: Update Files

Update these files in order:

### 1. `$LLM/huggingface-scripts/models.json`

Add model entry:

```json
{
  "modelId": "<HF_REPO_ID>",
  "localDir": "<HF_REPO_ID>",
  "include": ["<GGUF_FILE_PATTERNS_FOR_SELECTED_VARIANT>"]
}
```

### 2. `$LLM/launchers/<family>-mtp/<family>-catalog.ini` (or `<family>-mtp.ini`)

Add preset block. **Every value MUST have an inline comment with rationale** — cite HF README, blog, benchmark config, or note "inherited from convention" / "default — no guidance found".

**IMPORTANT**: Expand all path aliases to full paths before writing. `$HF` is a prompt alias only — the INI file uses absolute paths (e.g., `/Users/swordfish/.cache/huggingface/hub/...`):

```ini
[<modelId_or_alias>]
# https://huggingface.co/<HF_REPO_ID>

model = /Users/swordfish/.cache/huggingface/hub/<localDir>/<SELECTED_GGUF_FILE>.gguf
mmproj = /Users/swordfish/.cache/huggingface/hub/<localDir>/mmproj-*.gguf (if multimodal)
spec-draft-model = /Users/swordfish/.cache/huggingface/hub/<localDir>/MTP/... (if MTP)
alias = <HumanReadableName>, <tier-alias>

ctx-size = <contextWindow>
# Rationale: e.g., "262K native (HF README: --max-model-len 262144)" or "match existing preset pattern"

reasoning = on
# Rationale: e.g., "HF README: reasoning model with <think> blocks" or "off for non-reasoning variant"

chat-template-kwargs = {"enable_thinking":true/false}
# Rationale: e.g., "qwen3 parser (vLLM --reasoning-parser qwen3)" or "off for non-thinking preset"

presence-penalty = 0.0
# Rationale: e.g., "HF recommended for coding tasks" or "inherited from qwen3.6-catalog.ini convention — NOT in Ornith docs"

temperature = 0.6
# Rationale: e.g., "HF official quickstart: 0.6/0.95/20" or "benchmark reproduction uses 1.0"

top-p = 0.95
# Rationale: e.g., "HF official quickstart" or "SWE-Bench harness uses 0.95, Terminal-Bench uses 1.0"

top-k = 20
# Rationale: e.g., "HF official quickstart" or "default — no guidance found"

spec-type = none
# Rationale: e.g., "no MTP drafter in HF repo" or "draft-mtp (MTP file found at MTP/...)"
```

### 3. `$LLM/launchers/<family>-mtp/docs/<family>-model-routing.md`

Update or populate:

- Benchmarks table (if applicable)
- Decision matrix tier table (add new tier row)
- "How to choose" or equivalent section
- Sources section with HF links

### 4. `$PI/models.json`

**If this model family already has an existing provider** (qwen3.6, gemma-4, etc.), add the model entry under that provider block.

**If this is a new model family**, create a new provider block with the assigned port:

```json
"<family>@ai-gateway.swordfish.lan": {
  "baseUrl": "http://ai-gateway.swordfish.lan:<port>",
  "api": "openai-completions",
  "apiKey": "none",
  "models": [
    {
      "id": "<ModelIdentifier>",
      "name": "<tier-alias>",
      "reasoning": <true/false>,
      "input": ["text"] or ["text", "image"],
      "contextWindow": <contextWindow>,
      "maxTokens": <maxTokens>,
      "cost": { "input": <X>, "output": <5*X>, "cacheRead": <0.1*X>, "cacheWrite": <1.25*X> }
    }
  ]
}
```

### 5. `$PI/settings.json`

Add to `enabledModels` list: `<name>:<thinkingLevel>` (use `minimal`, `low`, `medium`, `high`, or `xhigh` based on use case).

### 6. `$PI/docs/models.md`

Update the documentation to reflect the new model:

- Add the new model family to the **Provider Architecture** section if it's a new provider.
- Add the model(s) to the **Model Categories** table under the appropriate family section.
- Update **Cost Tracking** table with the new model(s).
- Update the `enabledModels` JSON snippet in the Thinking Level Strategy section.
- If this is a new provider, add it to the **Inference Engine Details** table with its engine and thinking control info.

### 7. `$PI/docs/settings.md`

Update the documentation to reflect the new model:

- Update the **enabledModels** count in the key fields table (e.g., "6 aliases" → "11 aliases").
- Add the new model(s) to the **enabledModels** table with alias, technical ID, provider, and role.
- Update the **Model Selection Guide** table with new use cases and models.
- Update the **Thinking Level Rationale** section if the new model has unique thinking behavior (e.g., Ornith's ON reasoning with disabled CoT).
- Update the **thinking level decision matrix** table with new model types.

### 8. `$OMP/models.yml`

Update the llama provider block only — never touch `vllm.ai-gateway.swordfish`. Add the new model entry under `providers.llama.ai-gateway.swordfish.models`:

```yaml
- id: <ModelIdentifier>
  name: <tier-alias>
  reasoning: <true/false>
  input: [text] or [text, image]
  contextWindow: <contextWindow>
  maxTokens: <maxTokens>
  cost: { "input": <X>, "output": <5*X>, "cacheRead": <0.1*X>, "cacheWrite": <1.25*X> }
```

### 9. `$OMP/config.yml`

Sync model role assignments. Find all fields referencing `llama.ai-gateway.swordfish/` via grep and update as needed. Never modify `vllm.ai-gateway.swordfish/` references. Follow the sync rules in the plan document (add/edit/remove scenarios).

## Phase 7: Edit Existing Model Config (Edit Mode)

When the user provides `adjust` followed by natural-language field-value pairs for an existing model alias:

1. **Locate the model** in `$PI/models.json` under the correct provider block by matching the `name` field to the alias.
2. **Validate each field change**:
   - `contextWindow`: Must be a positive integer. For Qwen3.6, valid values are 80000, 120000, 150000, 262144 (native), or higher with YaRN.
   - `maxTokens`: Must be strictly less than `contextWindow`. Auto-adjust if the new value violates this constraint.
   - `cost` fields: Validate ratio consistency — `output = 5 × input`, `cacheRead = 0.1 × input`, `cacheWrite = 1.25 × input`.
   - `reasoning`: Boolean, no cross-field dependency.
   - `input`: Array of `["text"]` or `["text", "image"]`.
3. **PRE-FLIGHT: Inventory ALL occurrences of the old value** — before making ANY edits, run `grep -rn` searches across ALL affected files for the exact old value. This is mandatory. Do NOT skip this step.
   - `$PI/models.json` — grep for old value (e.g., `262144`, `131072`)
   - `$LLM/launchers/<family>-mtp/<family>-catalog.ini` — grep for old `ctx-size` value
   - `$PI/docs/models.md` — grep for old value (numeric and formatted, e.g., `262144`, `262,144`, `262K`)
   - `$LLM/launchers/<family>-mtp/README.md` — grep for old value
   - `$LLM/launchers/<family>-mtp/docs/<family>-model-routing.md` — grep for old value
   - `$OMP/models.yml` — grep for old model ID or alias under llama provider block
   - `$OMP/config.yml` — grep for old `llama.ai-gateway.swordfish/` reference
   - Print a summary: "Found old value in X files, Y total occurrences. Will update all."
4. **Update `$PI/models.json`** with the new values.
5. **Sync server-side catalog** if `contextWindow` changed:
   - Find the matching preset in `$LLM/launchers/<family>-mtp/<family>-catalog.ini` by alias.
   - Update `ctx-size` to match.
6. **Update documentation** — replace the old value in ALL occurrences found during pre-flight:
   - `$PI/docs/models.md` — Context Window Sizing table, rationale section, context window sizing rationale.
   - `$LLM/launchers/<family>-mtp/README.md` — preset tables, context descriptions.
   - `$LLM/launchers/<family>-mtp/docs/<family>-model-routing.md` — context window descriptions, preset lists, benchmark sections.
7. **Sync `.omp/agent` files**:
   - Update `$OMP/models.yml` under `providers.llama.ai-gateway.swordfish.models` with new values.
   - Update `$OMP/config.yml` — grep for all `llama.ai-gateway.swordfish/` references, update stale ones. Never touch `vllm.*`.
8. **Verify every occurrence was replaced** by running `grep` again after edits. If any old value remains, fix it.
9. **Confirm changes** to the user with a summary of what was updated across all files, listing each file and the number of occurrences replaced.

## Phase 8: Testing Instructions

After updates, instruct user to:

1. Run `./launcher-<family>.sh <preset-alias>` on DGX spark.
2. Test via local API at `ai-gateway.swordfish.lan:<port>`.
3. Verify model loads with correct `ctx-size` and `spec-type` settings.

## Constraints

- Do NOT commit or generate commit messages. User handles testing and commits.
- `maxTokens` must be strictly less than `contextWindow`.
- Only touch `llama.ai-gateway.swordfish` / `llama@ai-gateway.swordfish` blocks — never modify `vllm.*` references in any file.
- In `$OMP/config.yml`, use grep to find all `llama.ai-gateway.swordfish/` fields before editing; never modify `vllm.ai-gateway.swordfish/`.
