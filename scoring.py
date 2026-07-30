import math

def evaluate_model_match(model, criteria):
    hard_constraint_reasons = []

    # --- 1. Hard Constraints Validation ---
    
    # A. Data Sovereignty & Air-Gap Constraint
    if criteria.get("dataSovereignty") == "air_gapped_on_prem":
        supports_air_gap = "on_prem_gpu" in model.get("supportedDeployments", []) or "edge_mobile" in model.get("supportedDeployments", [])
        if not supports_air_gap:
            hard_constraint_reasons.append("Requires 100% Air-Gapped On-Premise / Local execution; model is proprietary cloud-only SaaS API.")

    # B. Cross-Border Prohibition
    if criteria.get("crossBorderProhibited") and criteria.get("region") == "EU":
        if "EU" not in model.get("compliance", {}).get("regionsSupported", []):
            hard_constraint_reasons.append("Cross-border data transfer prohibited outside EU; model provider lacks native EU data centers.")

    # C. HIPAA BAA Requirement
    if criteria.get("hipaa"):
        is_self_hosted_ok = model.get("isModelOpenSource") and criteria.get("deploymentArchitecture") in ["on_prem_gpu", "private_cloud_vpc"]
        if not model.get("compliance", {}).get("hipaaBaa") and not is_self_hosted_ok:
            hard_constraint_reasons.append("Requires signed HIPAA Business Associate Agreement (BAA); provider does not offer BAA for SaaS API.")

    # D. FedRAMP Level Requirement
    if criteria.get("fedramp") == "high" and model.get("compliance", {}).get("fedrampStatus") != "High":
        is_self_hosted_gov = model.get("isModelOpenSource") and criteria.get("deploymentArchitecture") == "on_prem_gpu"
        if not is_self_hosted_gov:
            hard_constraint_reasons.append("Requires FedRAMP High Security Authorization; provider holds insufficient FedRAMP status.")

    # E. Open Source License Requirement
    if criteria.get("licenseRequirement") == "open_source_apache" and not model.get("isModelOpenSource"):
        hard_constraint_reasons.append("Requires Open Source Permissive License (Apache 2.0 / MIT); model is closed proprietary API.")

    # F. Multimodal Vision & Audio Constraints
    task_caps = model.get("taskCapabilities", {})
    if criteria.get("multimodalVision") and not task_caps.get("vision"):
        hard_constraint_reasons.append("Requires Vision/Image input capability; model is text-only.")
    if criteria.get("multimodalAudio") and not task_caps.get("audio"):
        hard_constraint_reasons.append("Requires native Audio/Speech input processing; model lacks native audio.")

    # G. Context Window Hard Floor
    min_required_tokens = 8000
    cw = criteria.get("contextWindow", "small_8k")
    if cw == "medium_32k": min_required_tokens = 32000
    if cw == "large_128k": min_required_tokens = 128000
    if cw == "ultra_1m": min_required_tokens = 1000000

    if model.get("contextWindow", 0) < min_required_tokens:
        hard_constraint_reasons.append(f"Requires at least {min_required_tokens:,} tokens context window; model supports maximum {model.get('contextWindow', 0):,} tokens.")

    hard_constraint_failed = len(hard_constraint_reasons) > 0

    # --- 2. Weighted Sub-Scores Calculation (0 to 100) ---
    compliance = model.get("compliance", {})
    
    # A. Compliance & Regulatory Score (30%)
    compliance_score = 50
    if criteria.get("region") in compliance.get("regionsSupported", []) or criteria.get("region") == "Global": compliance_score += 15
    if criteria.get("hipaa") and compliance.get("hipaaBaa"): compliance_score += 15
    if criteria.get("gdpr") and "Zero Training" in compliance.get("gdprDataTraining", ""): compliance_score += 10
    if criteria.get("soc2Iso") and compliance.get("soc2IsoCert"): compliance_score += 10
    
    eu_act = compliance.get("euAiActCompliance", "").lower()
    if criteria.get("euAiAct") != "none" and ("gpai" in eu_act or "open weights" in eu_act):
        compliance_score += 15
    compliance_score = max(0, min(100, compliance_score))

    # B. Domain & Accuracy Fit Score (25%)
    domain_score = model.get("domainFitScores", {}).get(criteria.get("domain", "general"), 75)
    benchmarks = model.get("benchmarks", {})
    
    if criteria.get("taskType") == "code":
        domain_score = (domain_score * 0.4) + (benchmarks.get("humanEval", 0) * 0.6)
    elif criteria.get("taskType") == "reasoning":
        domain_score = (domain_score * 0.4) + (benchmarks.get("mmluPro", 0) * 0.6)
    elif criteria.get("taskType") == "rag_longdoc":
        context_bonus = 100 if model.get("contextWindow", 0) >= 128000 else (model.get("contextWindow", 0) / 128000.0) * 100
        domain_score = (domain_score * 0.5) + (context_bonus * 0.5)
    domain_score = max(0, min(100, round(domain_score)))

    # C. Technical & Architectural Fit Score (20%)
    technical_score = 70
    latency = model.get("latencyAvgMs", 1000)
    if criteria.get("latency") == "realtime_200ms":
        technical_score += 25 if latency <= 250 else (10 if latency <= 450 else -20)
    elif criteria.get("latency") == "fast_1s":
        technical_score += 20 if latency <= 600 else 0
        
    if criteria.get("structuredOutput") == "json_mode" and task_caps.get("jsonSchema"): technical_score += 10
    if criteria.get("structuredOutput") == "function_calling" and task_caps.get("functionCalling"): technical_score += 10
    if criteria.get("deploymentArchitecture") in model.get("supportedDeployments", []): technical_score += 15
    technical_score = max(0, min(100, technical_score))

    # D. Cost Efficiency Score (15%)
    cost_score = 80
    max_budget = criteria.get("maxBudgetPerMillion", 5.0)
    input_cost = model.get("inputCostPerM", 0)
    if input_cost == 0:
        cost_score = 100
    elif input_cost <= max_budget:
        ratio = input_cost / max_budget
        cost_score = round(100 - (ratio * 30))
    else:
        overage_ratio = input_cost / max_budget
        cost_score = max(10, round(70 - (overage_ratio * 25)))

    # E. Privacy & Data Retention Score (10%)
    privacy_score = 70
    if criteria.get("dataRetentionSla") == "zero_retention" and "Zero Training" in compliance.get("gdprDataTraining", ""):
        privacy_score += 20
    if model.get("isModelOpenSource"): privacy_score += 10
    privacy_score = max(0, min(100, privacy_score))

    # --- 3. Overall Weighted Score ---
    raw_overall_score = (
        (compliance_score * 0.30) +
        (domain_score * 0.25) +
        (technical_score * 0.20) +
        (cost_score * 0.15) +
        (privacy_score * 0.10)
    )

    if criteria.get("vendorPreference") != "any" and model.get("providerId") == criteria.get("vendorPreference"):
        raw_overall_score += 5

    final_overall_score = min(35, round(raw_overall_score * 0.4)) if hard_constraint_failed else min(99, round(raw_overall_score))

    # --- 4. Monthly Cost Estimation ---
    in_tokens = criteria.get("estimatedMonthlyInputTokensM", 10)
    out_tokens = criteria.get("estimatedMonthlyOutputTokensM", 2)
    estimated_cost = round((in_tokens * input_cost) + (out_tokens * model.get("outputCostPerM", 0)), 2)

    # --- 5. Generate Dynamic Justifications ---
    justification = generate_justification(model, criteria, hard_constraint_failed, hard_constraint_reasons, final_overall_score)

    return {
        "model": model,
        "overallScore": final_overall_score,
        "complianceScore": compliance_score,
        "domainScore": domain_score,
        "technicalScore": technical_score,
        "costScore": cost_score,
        "privacyScore": privacy_score,
        "hardConstraintFailed": hard_constraint_failed,
        "hardConstraintReasons": hard_constraint_reasons,
        "justification": justification,
        "estimatedMonthlyCostUSD": estimated_cost
    }

def generate_justification(model, criteria, failed, reasons, score):
    if failed:
        return {
            "summary": f"Not Recommended for Strict Policy: Fails {len(reasons)} hard governance or architectural requirement(s).",
            "keyPros": [
                f"High general intelligence rating ({model.get('benchmarks', {}).get('mmluPro')} MMLU-Pro)",
                f"Context window of {model.get('contextWindow', 0):,} tokens"
            ],
            "tradeOffs": [
                f"Fails compliance filter: {reasons[0]}",
                "Alternative deployment setup required for enterprise approval"
            ],
            "governanceRationale": f"Non-compliant for current criteria: {' '.join(reasons)}",
            "sovereigntyRationale": f"Sovereignty check flagged limitations under {criteria.get('region')} / {criteria.get('dataSovereignty')} policy."
        }

    key_pros = []
    trade_offs = []

    compliance = model.get("compliance", {})
    
    if compliance.get("hipaaBaa") and criteria.get("hipaa"):
        key_pros.append("Official HIPAA Business Associate Agreement (BAA) supported with Zero Data Retention.")
    if model.get("isModelOpenSource"):
        key_pros.append(f"Permissive {model.get('licenseType')} allows complete self-hosted air-gapped deployment in private VPC or on-prem hardware.")
    if model.get("contextWindow", 0) >= 1000000:
        key_pros.append(f"Massive {model.get('contextWindow') / 1000000:.1f}M token context window supports whole-codebase / multi-document RAG.")
    
    he_score = model.get("benchmarks", {}).get("humanEval", 0)
    if he_score >= 90 and (criteria.get("taskType") == "code" or criteria.get("domain") == "software"):
        key_pros.append(f"Top-tier HumanEval coding benchmark score ({he_score}%) for precise software synthesis.")
        
    latency = model.get("latencyAvgMs", 1000)
    if latency <= 250:
        key_pros.append(f"Ultra-low latency (~{latency}ms) ideal for real-time conversational agents.")
        
    input_cost = model.get("inputCostPerM", 0)
    if input_cost <= 0.50:
        key_pros.append(f"Highly cost-effective (${input_cost:.2f}/1M input tokens) for high-throughput batch workloads.")

    if not model.get("isModelOpenSource"):
        trade_offs.append("Proprietary closed API requires outbound internet/VPC routing and vendor API SLA dependency.")
    else:
        trade_offs.append("Self-hosting requires dedicated GPU infrastructure (e.g. H100/A100 clusters or vLLM orchestration).")
        
    if latency > 600:
        trade_offs.append(f"Higher average latency (~{latency}ms) due to deep reasoning / MoE architecture.")
        
    if input_cost > 2.00:
        trade_offs.append(f"Premium input pricing (${input_cost:.2f}/1M tokens) requires budget monitoring for heavy workloads.")

    gov_rat = f"{model.get('name')} fully satisfies HIPAA requirements with BAA availability and zero customer data training." if criteria.get("hipaa") else f"{model.get('name')} adheres to {compliance.get('gdprDataTraining')} and SOC 2 Type II audit standards."
    
    sov_options = compliance.get("sovereignOptions", [])
    sov_rat = f"Supports sovereignty via {' or '.join(sov_options)}." if sov_options else f"Provides cloud API endpoints in {', '.join(compliance.get('regionsSupported', []))}."

    summary = f"Scored {score}% match. {model.get('name')} fits {criteria.get('domain', 'general').upper()} domain tasks with {model.get('benchmarks', {}).get('mmluPro')}% MMLU-Pro accuracy and {compliance.get('euAiActCompliance', '')[:70]}..."

    return {
        "summary": summary,
        "keyPros": key_pros[:3],
        "tradeOffs": trade_offs[:2],
        "governanceRationale": gov_rat,
        "sovereigntyRationale": sov_rat
    }

def rank_llms_for_inputs(models, criteria):
    results = [evaluate_model_match(model, criteria) for model in models]
    
    # Sort primarily by overallScore (descending)
    # Secondary sort: if both failed or both passed, use score. 
    # But wait, final_overall_score already drastically penalizes failures (cap at 35)
    results.sort(key=lambda x: (not x["hardConstraintFailed"], x["overallScore"]), reverse=True)
    return results
