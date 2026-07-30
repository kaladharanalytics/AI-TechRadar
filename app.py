import streamlit as st
import pandas as pd
import altair as alt
import requests
import math
import json
from typing import List, Dict, Any

CURATED_MODELS_DB = [
    {
        "id": "gpt-4o",
        "name": "OpenAI GPT-4o",
        "provider": "OpenAI",
        "providerId": "openai",
        "badge": "Frontier Multimodal",
        "description": "Flagship omni model with native vision, audio, strict JSON mode, and high reasoning throughput across multimodal benchmarks.",
        "contextWindow": 128000,
        "latencyAvgMs": 450,
        "inputCostPerM": 2.5,
        "outputCostPerM": 10,
        "parameterSize": "Proprietary MoE",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "General Purpose AI & High-Risk system support via Azure OpenAI & Enterprise SLA",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "Azure OpenAI Dedicated VPC",
                "Azure Government Cloud"
            ]
        },
        "benchmarks": {
            "mmluPro": 88.6,
            "humanEval": 90.2,
            "gpqa": 53.6,
            "mathGsm8k": 95.8,
            "lmsysArenaElo": 1340
        },
        "domainFitScores": {
            "healthcare": 92,
            "finance": 95,
            "legal": 94,
            "software": 96,
            "ecommerce": 95,
            "defense": 90,
            "research": 94,
            "education": 95,
            "general": 98
        },
        "taskCapabilities": {
            "vision": True,
            "audio": True,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "OpenAI GPT-4o Official Overview & Specs",
                "url": "https://platform.openai.com/docs/models/gpt-4o",
                "type": "official_docs"
            },
            {
                "title": "OpenAI Enterprise Privacy & Compliance Commitments",
                "url": "https://openai.com/enterprise-privacy/",
                "type": "compliance_page"
            },
            {
                "title": "Azure OpenAI Service FedRAMP & HIPAA Documentation",
                "url": "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/compliance",
                "type": "compliance_page"
            },
            {
                "title": "LMSYS Chatbot Arena Leaderboard",
                "url": "https://chat.lmsys.org/?leaderboard",
                "type": "leaderboard"
            }
        ],
        "releaseDate": "Apr 2023"
    },
    {
        "id": "claude-3-5-sonnet",
        "name": "Anthropic Claude 3.5 Sonnet",
        "provider": "Anthropic",
        "providerId": "anthropic",
        "badge": "Coding & Reasoning Champion",
        "description": "Industry benchmark leader for software engineering, complex multi-step reasoning, long document analysis, and precise tool call execution.",
        "contextWindow": 200000,
        "latencyAvgMs": 500,
        "inputCostPerM": 3,
        "outputCostPerM": 15,
        "parameterSize": "Proprietary",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance with Systemic Risk Disclosures & EU Cloud Hosting (AWS Bedrock / GCP Vertex)",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "AWS Bedrock EU (Frankfurt)",
                "GCP Vertex AI Dedicated VPC",
                "AWS GovCloud"
            ]
        },
        "benchmarks": {
            "mmluPro": 89.2,
            "humanEval": 93.7,
            "gpqa": 65,
            "mathGsm8k": 96.4,
            "lmsysArenaElo": 1350
        },
        "domainFitScores": {
            "healthcare": 94,
            "finance": 96,
            "legal": 98,
            "software": 99,
            "ecommerce": 93,
            "defense": 91,
            "research": 97,
            "education": 96,
            "general": 97
        },
        "taskCapabilities": {
            "vision": True,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "Anthropic Claude 3.5 Sonnet Announcement & Benchmarks",
                "url": "https://www.anthropic.com/news/claude-3-5-sonnet",
                "type": "official_docs"
            },
            {
                "title": "Anthropic Trust Portal & HIPAA Compliance",
                "url": "https://trust.anthropic.com/",
                "type": "compliance_page"
            },
            {
                "title": "AWS Bedrock FedRAMP & Compliance Documentation",
                "url": "https://aws.amazon.com/bedrock/compliance/",
                "type": "compliance_page"
            }
        ],
        "releaseDate": "May 2025"
    },
    {
        "id": "gemini-1-5-pro",
        "name": "Google Gemini 1.5 Pro",
        "provider": "Google DeepMind",
        "providerId": "google",
        "badge": "2M Token Context & Multimodal",
        "description": "Breakthrough 2-million token context window capable of ingesting entire codebases, multi-hour videos, and large technical manuals natively.",
        "contextWindow": 2000000,
        "latencyAvgMs": 650,
        "inputCostPerM": 1.25,
        "outputCostPerM": 5,
        "parameterSize": "Proprietary MoE",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance with Google Cloud Assured Workloads EU",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "GCP Assured Workloads EU",
                "Google Cloud Private VPC"
            ]
        },
        "benchmarks": {
            "mmluPro": 85.9,
            "humanEval": 84.1,
            "gpqa": 59.1,
            "mathGsm8k": 90.8,
            "lmsysArenaElo": 1315
        },
        "domainFitScores": {
            "healthcare": 93,
            "finance": 92,
            "legal": 96,
            "software": 91,
            "ecommerce": 90,
            "defense": 94,
            "research": 98,
            "education": 94,
            "general": 94
        },
        "taskCapabilities": {
            "vision": True,
            "audio": True,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "Google DeepMind Gemini 1.5 Technical Paper",
                "url": "https://deepmind.google/technologies/gemini/pro/",
                "type": "paper"
            },
            {
                "title": "Google Cloud Vertex AI HIPAA & BAA Security Overview",
                "url": "https://cloud.google.com/security/compliance/hipaa",
                "type": "compliance_page"
            }
        ],
        "releaseDate": "Sep 2025"
    },
    {
        "id": "deepseek-r1",
        "name": "DeepSeek R1",
        "provider": "DeepSeek",
        "providerId": "deepseek",
        "badge": "Reasoning & Open Weights",
        "description": "State-of-the-art open weights reasoning model trained via large-scale reinforcement learning, matching GPT-o1 on math, coding, and logical reasoning.",
        "contextWindow": 128000,
        "latencyAvgMs": 1200,
        "inputCostPerM": 0.55,
        "outputCostPerM": 2.19,
        "parameterSize": "671B (37B active MoE)",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": True,
        "licenseType": "MIT License (Open Weights)",
        "compliance": {
            "hipaaBaa": False,
            "euAiActCompliance": "Fully Open Weights - Self-hostable inside EU borders to meet 100% Data Sovereignty",
            "nistRmfCompliant": True,
            "fedrampStatus": "None",
            "gdprDataTraining": "Self-hosted Zero Retention",
            "soc2IsoCert": False,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "MiddleEast",
                "LatAm",
                "Global"
            ],
            "sovereignOptions": [
                "100% On-Premise GPU Cluster",
                "Self-Hosted vLLM / SGLang in Private VPC"
            ]
        },
        "benchmarks": {
            "mmluPro": 84,
            "humanEval": 90.8,
            "gpqa": 71.5,
            "mathGsm8k": 97.3,
            "lmsysArenaElo": 1360
        },
        "domainFitScores": {
            "healthcare": 86,
            "finance": 95,
            "legal": 88,
            "software": 98,
            "ecommerce": 85,
            "defense": 89,
            "research": 99,
            "education": 96,
            "general": 92
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "DeepSeek-R1 GitHub Repository & Technical Report",
                "url": "https://github.com/deepseek-ai/DeepSeek-R1",
                "type": "official_docs"
            },
            {
                "title": "DeepSeek-R1 ArXiv Paper (2501.12948)",
                "url": "https://arxiv.org/abs/2501.12948",
                "type": "paper"
            },
            {
                "title": "Hugging Face DeepSeek-R1 Model Weights & MIT License",
                "url": "https://huggingface.co/deepseek-ai/DeepSeek-R1",
                "type": "model_card"
            }
        ],
        "releaseDate": "Jul 2023"
    },
    {
        "id": "deepseek-v3",
        "name": "DeepSeek V3",
        "provider": "DeepSeek",
        "providerId": "deepseek",
        "badge": "Ultra-High Efficiency MoE",
        "description": "671B parameter Mixture-of-Experts model providing top-tier general intelligence and coding at unprecedented cost efficiency.",
        "contextWindow": 128000,
        "latencyAvgMs": 400,
        "inputCostPerM": 0.14,
        "outputCostPerM": 0.28,
        "parameterSize": "671B (37B active MoE)",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": True,
        "licenseType": "MIT License (Open Weights)",
        "compliance": {
            "hipaaBaa": False,
            "euAiActCompliance": "Open Weights - Deployable inside EU data boundaries",
            "nistRmfCompliant": True,
            "fedrampStatus": "None",
            "gdprDataTraining": "Self-hosted Zero Retention",
            "soc2IsoCert": False,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "MiddleEast",
                "LatAm",
                "Global"
            ],
            "sovereignOptions": [
                "100% On-Premise GPU Cluster",
                "Private Cloud vLLM Deployment"
            ]
        },
        "benchmarks": {
            "mmluPro": 88.5,
            "humanEval": 89.1,
            "gpqa": 59.1,
            "mathGsm8k": 95.3,
            "lmsysArenaElo": 1320
        },
        "domainFitScores": {
            "healthcare": 87,
            "finance": 93,
            "legal": 90,
            "software": 95,
            "ecommerce": 94,
            "defense": 88,
            "research": 95,
            "education": 94,
            "general": 95
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "DeepSeek-V3 Technical Repository",
                "url": "https://github.com/deepseek-ai/DeepSeek-V3",
                "type": "official_docs"
            },
            {
                "title": "Hugging Face DeepSeek-V3",
                "url": "https://huggingface.co/deepseek-ai/DeepSeek-V3",
                "type": "model_card"
            }
        ],
        "releaseDate": "Apr 2023"
    },
    {
        "id": "llama-3-3-70b",
        "name": "Meta Llama 3.3 70B Instruct",
        "provider": "Meta",
        "providerId": "meta",
        "badge": "Enterprise Open Weights Standard",
        "description": "Meta's premier 70B parameter model delivering performance comparable to Llama 3.1 405B with drastically lower memory and latency requirements.",
        "contextWindow": 128000,
        "latencyAvgMs": 350,
        "inputCostPerM": 0.4,
        "outputCostPerM": 0.4,
        "parameterSize": "70B Dense",
        "parameterClass": "mid_30b_70b",
        "isModelOpenSource": True,
        "licenseType": "Llama 3.3 Community License (Permissive Commercial)",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "Fully Open Weights - Complete EU Data Sovereignty via Local Hosting",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data (Self-hosted or Cloud BAA)",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "MiddleEast",
                "LatAm",
                "Global"
            ],
            "sovereignOptions": [
                "Self-Hosted On-Premise",
                "AWS EU Sovereign Cloud",
                "Azure Government"
            ]
        },
        "benchmarks": {
            "mmluPro": 86.4,
            "humanEval": 88.6,
            "gpqa": 52.8,
            "mathGsm8k": 93,
            "lmsysArenaElo": 1310
        },
        "domainFitScores": {
            "healthcare": 90,
            "finance": 92,
            "legal": 91,
            "software": 92,
            "ecommerce": 93,
            "defense": 95,
            "research": 93,
            "education": 93,
            "general": 94
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "Meta AI Llama 3.3 Announcement",
                "url": "https://ai.meta.com/blog/llama-3-3/",
                "type": "official_docs"
            },
            {
                "title": "Hugging Face Meta Llama 3.3 70B Instruct",
                "url": "https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct",
                "type": "model_card"
            },
            {
                "title": "Meta Llama 3 Governance & Acceptable Use Policy",
                "url": "https://github.com/meta-llama/llama-models",
                "type": "compliance_page"
            }
        ],
        "releaseDate": "Jul 2024"
    },
    {
        "id": "qwen-2-5-72b",
        "name": "Alibaba Qwen 2.5 72B Instruct",
        "provider": "Alibaba Cloud",
        "providerId": "qwen",
        "badge": "Multilingual & Code Powerhouse",
        "description": "Top-ranking open-weights model specialized in 29+ languages, deep coding comprehension, complex math, and structured data generation.",
        "contextWindow": 128000,
        "latencyAvgMs": 380,
        "inputCostPerM": 0.35,
        "outputCostPerM": 0.4,
        "parameterSize": "72B Dense",
        "parameterClass": "mid_30b_70b",
        "isModelOpenSource": True,
        "licenseType": "Qwen License (Permissive Commercial)",
        "compliance": {
            "hipaaBaa": False,
            "euAiActCompliance": "Deployable on local EU infrastructure for total data localization",
            "nistRmfCompliant": True,
            "fedrampStatus": "None",
            "gdprDataTraining": "Self-hosted Zero Retention",
            "soc2IsoCert": False,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "MiddleEast",
                "Global"
            ],
            "sovereignOptions": [
                "On-Premise GPU Nodes",
                "Private Cloud vLLM / TensorRT-LLM"
            ]
        },
        "benchmarks": {
            "mmluPro": 86.8,
            "humanEval": 86.6,
            "gpqa": 54.1,
            "mathGsm8k": 93.8,
            "lmsysArenaElo": 1305
        },
        "domainFitScores": {
            "healthcare": 85,
            "finance": 90,
            "legal": 87,
            "software": 94,
            "ecommerce": 96,
            "defense": 82,
            "research": 92,
            "education": 92,
            "general": 93
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "Qwen 2.5 Official Blog & Benchmark Data",
                "url": "https://qwenlm.github.io/blog/qwen2.5/",
                "type": "official_docs"
            },
            {
                "title": "Hugging Face Qwen 2.5 72B Instruct Model Card",
                "url": "https://huggingface.co/Qwen/Qwen2.5-72B-Instruct",
                "type": "model_card"
            }
        ],
        "releaseDate": "Apr 2025"
    },
    {
        "id": "mistral-large-2",
        "name": "Mistral Large 2 (2407)",
        "provider": "Mistral AI",
        "providerId": "mistral",
        "badge": "EU Native & Multilingual",
        "description": "European frontier model boasting native fluency in French, German, Spanish, Italian, and 80+ coding languages, designed for strict EU compliance.",
        "contextWindow": 128000,
        "latencyAvgMs": 420,
        "inputCostPerM": 2,
        "outputCostPerM": 6,
        "parameterSize": "123B Dense",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": False,
        "licenseType": "Mistral Research & Commercial License",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "Native EU AI Act Sovereign Compliance with European Cloud Datacenters",
            "nistRmfCompliant": True,
            "fedrampStatus": "Moderate",
            "gdprDataTraining": "Zero Training on Customer Data (EU Sovereign Privacy)",
            "soc2IsoCert": True,
            "regionsSupported": [
                "EU",
                "US",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "Mistral EU Cloud (Paris/Frankfurt)",
                "Azure OpenAI EU",
                "AWS Bedrock EU"
            ]
        },
        "benchmarks": {
            "mmluPro": 84,
            "humanEval": 92,
            "gpqa": 49.3,
            "mathGsm8k": 91.5,
            "lmsysArenaElo": 1300
        },
        "domainFitScores": {
            "healthcare": 89,
            "finance": 94,
            "legal": 95,
            "software": 95,
            "ecommerce": 92,
            "defense": 88,
            "research": 91,
            "education": 91,
            "general": 93
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "Mistral Large 2 Release Announcement",
                "url": "https://mistral.ai/news/mistral-large-2407/",
                "type": "official_docs"
            },
            {
                "title": "Mistral AI Documentation & Compliance",
                "url": "https://docs.mistral.ai/getting-started/models/",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Dec 2023"
    },
    {
        "id": "gpt-4o-mini",
        "name": "OpenAI GPT-4o-mini",
        "provider": "OpenAI",
        "providerId": "openai",
        "badge": "Ultra-Fast & Affordable",
        "description": "High-speed, low-cost multimodal model optimized for lightweight tasks, customer support, and fast structured extraction.",
        "contextWindow": 128000,
        "latencyAvgMs": 220,
        "inputCostPerM": 0.15,
        "outputCostPerM": 0.6,
        "parameterSize": "Small Proprietary",
        "parameterClass": "small_7b_14b",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance via Enterprise SLA / Azure OpenAI",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "Azure OpenAI Dedicated VPC"
            ]
        },
        "benchmarks": {
            "mmluPro": 82,
            "humanEval": 87.2,
            "gpqa": 40.2,
            "mathGsm8k": 87,
            "lmsysArenaElo": 1275
        },
        "domainFitScores": {
            "healthcare": 82,
            "finance": 85,
            "legal": 80,
            "software": 86,
            "ecommerce": 95,
            "defense": 80,
            "research": 82,
            "education": 88,
            "general": 90
        },
        "taskCapabilities": {
            "vision": True,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "OpenAI GPT-4o-mini Release & Cost Specs",
                "url": "https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Aug 2025"
    },
    {
        "id": "gemini-1-5-flash",
        "name": "Google Gemini 1.5 Flash",
        "provider": "Google DeepMind",
        "providerId": "google",
        "badge": "Sub-300ms Speed & 1M Context",
        "description": "Lightweight multimodal model optimized for ultra-low latency, real-time voice/chat pipelines, and high-frequency document processing.",
        "contextWindow": 1000000,
        "latencyAvgMs": 200,
        "inputCostPerM": 0.075,
        "outputCostPerM": 0.3,
        "parameterSize": "Small Proprietary",
        "parameterClass": "small_7b_14b",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance with GCP Assured Workloads",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "GCP Assured Workloads EU"
            ]
        },
        "benchmarks": {
            "mmluPro": 79.1,
            "humanEval": 74.3,
            "gpqa": 37.1,
            "mathGsm8k": 84.5,
            "lmsysArenaElo": 1260
        },
        "domainFitScores": {
            "healthcare": 83,
            "finance": 84,
            "legal": 82,
            "software": 80,
            "ecommerce": 96,
            "defense": 85,
            "research": 86,
            "education": 89,
            "general": 91
        },
        "taskCapabilities": {
            "vision": True,
            "audio": True,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "Google DeepMind Gemini 1.5 Flash Product Page",
                "url": "https://deepmind.google/technologies/gemini/flash/",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Sep 2023"
    },
    {
        "id": "claude-3-5-haiku",
        "name": "Anthropic Claude 3.5 Haiku",
        "provider": "Anthropic",
        "providerId": "anthropic",
        "badge": "Lightning Speed & Precision",
        "description": "Fastest model in the Claude 3.5 family, outperforming Claude 3 Opus on standard coding benchmarks while operating at near real-time speeds.",
        "contextWindow": 200000,
        "latencyAvgMs": 210,
        "inputCostPerM": 0.8,
        "outputCostPerM": 4,
        "parameterSize": "Small Proprietary",
        "parameterClass": "small_7b_14b",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance via AWS Bedrock & GCP Vertex",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "AWS Bedrock EU",
                "AWS GovCloud"
            ]
        },
        "benchmarks": {
            "mmluPro": 80.5,
            "humanEval": 88.1,
            "gpqa": 41.5,
            "mathGsm8k": 88.9,
            "lmsysArenaElo": 1285
        },
        "domainFitScores": {
            "healthcare": 86,
            "finance": 88,
            "legal": 86,
            "software": 92,
            "ecommerce": 94,
            "defense": 86,
            "research": 87,
            "education": 90,
            "general": 92
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "Anthropic Claude 3.5 Haiku Release & Benchmarks",
                "url": "https://www.anthropic.com/news/claude-3-5-haiku",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Feb 2023"
    },
    {
        "id": "codestral-22b",
        "name": "Mistral Codestral 22B",
        "provider": "Mistral AI",
        "providerId": "mistral",
        "badge": "Dedicated Code & Fill-in-Middle",
        "description": "Open-weights coding model fluent in 80+ programming languages with fill-in-the-middle capability for IDE autocompletion.",
        "contextWindow": 32000,
        "latencyAvgMs": 250,
        "inputCostPerM": 0.2,
        "outputCostPerM": 0.6,
        "parameterSize": "22B Dense",
        "parameterClass": "small_7b_14b",
        "isModelOpenSource": True,
        "licenseType": "Mistral Non-Commercial / Commercial License",
        "compliance": {
            "hipaaBaa": False,
            "euAiActCompliance": "Open Weights - EU Local Hosting Compliant",
            "nistRmfCompliant": True,
            "fedrampStatus": "None",
            "gdprDataTraining": "Self-hosted Zero Retention",
            "soc2IsoCert": False,
            "regionsSupported": [
                "EU",
                "US",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "On-Premise IDE Integration",
                "Local Ollama / vLLM"
            ]
        },
        "benchmarks": {
            "mmluPro": 78.2,
            "humanEval": 81.1,
            "gpqa": 38.5,
            "mathGsm8k": 82,
            "lmsysArenaElo": 1240
        },
        "domainFitScores": {
            "healthcare": 70,
            "finance": 80,
            "legal": 75,
            "software": 98,
            "ecommerce": 80,
            "defense": 80,
            "research": 85,
            "education": 85,
            "general": 85
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "Mistral Codestral Official Announcement",
                "url": "https://mistral.ai/news/codestral/",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Aug 2025"
    },
    {
        "id": "phi-4-14b",
        "name": "Microsoft Phi-4 14B",
        "provider": "Microsoft",
        "providerId": "google",
        "badge": "Synthetic Data & Reasoning Specialist",
        "description": "14B parameter small language model trained on synthetic data, achieving benchmarks competitive with 70B models at lightweight compute footprint.",
        "contextWindow": 16000,
        "latencyAvgMs": 180,
        "inputCostPerM": 0.1,
        "outputCostPerM": 0.2,
        "parameterSize": "14B Dense",
        "parameterClass": "small_7b_14b",
        "isModelOpenSource": True,
        "licenseType": "MIT License",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "Open Weights MIT License - Local On-Premise EU Deployment",
            "nistRmfCompliant": True,
            "fedrampStatus": "Moderate",
            "gdprDataTraining": "Self-hosted Zero Retention",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "Edge / Local Device",
                "Azure Private VPC",
                "On-Premise GPU"
            ]
        },
        "benchmarks": {
            "mmluPro": 84.4,
            "humanEval": 82.3,
            "gpqa": 54,
            "mathGsm8k": 92.5,
            "lmsysArenaElo": 1280
        },
        "domainFitScores": {
            "healthcare": 80,
            "finance": 85,
            "legal": 82,
            "software": 90,
            "ecommerce": 85,
            "defense": 88,
            "research": 93,
            "education": 92,
            "general": 89
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc",
            "on_prem_gpu",
            "edge_mobile"
        ],
        "references": [
            {
                "title": "Hugging Face Microsoft Phi-4 Model Card",
                "url": "https://huggingface.co/microsoft/phi-4",
                "type": "model_card"
            }
        ],
        "releaseDate": "Jan 2024"
    },
    {
        "id": "llama-3-2-3b-edge",
        "name": "Meta Llama 3.2 3B Instruct (Edge)",
        "provider": "Meta",
        "providerId": "meta",
        "badge": "On-Device Edge & Mobile",
        "description": "Lightweight 3B model optimized for local on-device inference, mobile apps, offline edge hardware, and zero-network privacy environments.",
        "contextWindow": 128000,
        "latencyAvgMs": 90,
        "inputCostPerM": 0,
        "outputCostPerM": 0,
        "parameterSize": "3.2B Dense",
        "parameterClass": "mobile_3b",
        "isModelOpenSource": True,
        "licenseType": "Llama 3.2 Community License",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "100% Local On-Device Air-Gapped Execution - Zero Cloud Data Transmission",
            "nistRmfCompliant": True,
            "fedrampStatus": "High",
            "gdprDataTraining": "100% Offline Local Data Processing",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "MiddleEast",
                "LatAm",
                "Global"
            ],
            "sovereignOptions": [
                "100% On-Device Offline (iOS/Android/Laptop)",
                "Local Ollama / MLX / ExecuTorch"
            ]
        },
        "benchmarks": {
            "mmluPro": 63.4,
            "humanEval": 68.3,
            "gpqa": 32.1,
            "mathGsm8k": 77.2,
            "lmsysArenaElo": 1180
        },
        "domainFitScores": {
            "healthcare": 78,
            "finance": 75,
            "legal": 70,
            "software": 80,
            "ecommerce": 88,
            "defense": 92,
            "research": 72,
            "education": 82,
            "general": 84
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "edge_mobile",
            "on_prem_gpu"
        ],
        "references": [
            {
                "title": "Meta AI Llama 3.2 Edge & Mobile Announcement",
                "url": "https://ai.meta.com/blog/llama-3-2-connect-2024/",
                "type": "official_docs"
            },
            {
                "title": "Hugging Face Llama 3.2 3B Instruct",
                "url": "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct",
                "type": "model_card"
            }
        ],
        "releaseDate": "Aug 2025"
    },
    {
        "id": "cohere-command-r-plus",
        "name": "Cohere Command R+",
        "provider": "Cohere",
        "providerId": "cohere",
        "badge": "Enterprise RAG & Citations",
        "description": "Enterprise model purpose-built for Retrieval-Augmented Generation (RAG) with verifiable inline citations and 10-language business fluency.",
        "contextWindow": 128000,
        "latencyAvgMs": 460,
        "inputCostPerM": 2.5,
        "outputCostPerM": 10,
        "parameterSize": "104B Dense",
        "parameterClass": "frontier_100b_moe",
        "isModelOpenSource": False,
        "licenseType": "CC-BY-NC / Enterprise License",
        "compliance": {
            "hipaaBaa": True,
            "euAiActCompliance": "GPAI Compliance with Private VPC Cloud Hosting (Azure/AWS/Oracle)",
            "nistRmfCompliant": True,
            "fedrampStatus": "Moderate",
            "gdprDataTraining": "Zero Training on Customer Data",
            "soc2IsoCert": True,
            "regionsSupported": [
                "US",
                "EU",
                "APAC",
                "Global"
            ],
            "sovereignOptions": [
                "Azure Private VPC",
                "AWS Bedrock",
                "Oracle Cloud Infrastructure"
            ]
        },
        "benchmarks": {
            "mmluPro": 81.5,
            "humanEval": 79.4,
            "gpqa": 42,
            "mathGsm8k": 84,
            "lmsysArenaElo": 1270
        },
        "domainFitScores": {
            "healthcare": 91,
            "finance": 94,
            "legal": 96,
            "software": 88,
            "ecommerce": 92,
            "defense": 89,
            "research": 93,
            "education": 90,
            "general": 91
        },
        "taskCapabilities": {
            "vision": False,
            "audio": False,
            "code": True,
            "reasoning": True,
            "jsonSchema": True,
            "functionCalling": True
        },
        "supportedDeployments": [
            "saas_api",
            "private_cloud_vpc"
        ],
        "references": [
            {
                "title": "Cohere Command R+ Technical Blog & Benchmarks",
                "url": "https://cohere.com/blog/command-r-plus-microsoft-azure",
                "type": "official_docs"
            },
            {
                "title": "Cohere Enterprise Documentation",
                "url": "https://docs.cohere.com/docs/command-r-plus",
                "type": "official_docs"
            }
        ],
        "releaseDate": "Apr 2023"
    },
    {
        "id": "kimi-k3",
        "name": "Kimi K3",
        "provider": "Moonshot AI",
        "isModelOpenSource": False,
        "licenseType": "Proprietary",
        "domainSpecialty": [
            "general",
            "research",
            "software"
        ],
        "taskSpecialty": [
            "chat",
            "reasoning",
            "rag_longdoc"
        ],
        "multimodalVision": True,
        "multimodalAudio": False,
        "contextWindow": 1000000,
        "latencyAvgMs": 800,
        "structuredOutputSupport": [
            "json_mode",
            "function_calling"
        ],
        "deploymentArchitecture": [
            "saas_api"
        ],
        "inputCostPerM": 2.5,
        "outputCostPerM": 7.5,
        "compliance": {
            "hipaaCompliant": False,
            "fedrampLevel": "none",
            "euAiAct": "gpai_standard",
            "gdprCompliant": True,
            "soc2Iso27001": True,
            "nistRmfAligned": False
        },
        "dataPrivacy": {
            "dataSovereigntyOptions": [
                "standard_cloud"
            ],
            "crossBorderProhibited": False,
            "dataRetentionSla": "zero_retention",
            "customerManagedKeys": False
        },
        "geography": [
            "Global",
            "APAC",
            "US"
        ],
        "releaseDate": "July 2026"
    },
    {
        "id": "gpt-5.6",
        "name": "GPT-5.6",
        "provider": "OpenAI",
        "isModelOpenSource": False,
        "licenseType": "Proprietary API",
        "domainSpecialty": [
            "general",
            "software",
            "healthcare",
            "finance",
            "legal",
            "defense"
        ],
        "taskSpecialty": [
            "chat",
            "code",
            "reasoning",
            "rag_longdoc",
            "agentic_workflow"
        ],
        "multimodalVision": True,
        "multimodalAudio": True,
        "contextWindow": 1000000,
        "latencyAvgMs": 350,
        "structuredOutputSupport": [
            "json_mode",
            "function_calling"
        ],
        "deploymentArchitecture": [
            "saas_api",
            "dedicated_vpc"
        ],
        "inputCostPerM": 10.0,
        "outputCostPerM": 30.0,
        "compliance": {
            "hipaaCompliant": True,
            "fedrampLevel": "high",
            "euAiAct": "high_risk_system",
            "gdprCompliant": True,
            "soc2Iso27001": True,
            "nistRmfAligned": True
        },
        "dataPrivacy": {
            "dataSovereigntyOptions": [
                "standard_cloud",
                "dedicated_vpc"
            ],
            "crossBorderProhibited": False,
            "dataRetentionSla": "zero_retention",
            "customerManagedKeys": True
        },
        "geography": [
            "US",
            "EU",
            "Global"
        ],
        "releaseDate": "June 2026"
    },
    {
        "id": "fable-5",
        "name": "Fable 5",
        "provider": "Fable AI",
        "isModelOpenSource": True,
        "licenseType": "APACHE-2.0",
        "domainSpecialty": [
            "creative_writing",
            "general"
        ],
        "taskSpecialty": [
            "chat",
            "creative_writing"
        ],
        "multimodalVision": False,
        "multimodalAudio": False,
        "contextWindow": 128000,
        "latencyAvgMs": 450,
        "structuredOutputSupport": [
            "none"
        ],
        "deploymentArchitecture": [
            "saas_api",
            "on_prem_gpu"
        ],
        "inputCostPerM": 1.0,
        "outputCostPerM": 2.0,
        "compliance": {
            "hipaaCompliant": False,
            "fedrampLevel": "none",
            "euAiAct": "none",
            "gdprCompliant": True,
            "soc2Iso27001": False,
            "nistRmfAligned": False
        },
        "dataPrivacy": {
            "dataSovereigntyOptions": [
                "air_gapped_on_prem"
            ],
            "crossBorderProhibited": True,
            "dataRetentionSla": "customer_managed_keys",
            "customerManagedKeys": True
        },
        "geography": [
            "Global",
            "US"
        ],
        "releaseDate": "May 2026"
    }
]

# --- hf_api.py ---


def fetch_top_10000_models():
    """
    Fetches the top 10000 trending models from Hugging Face by paginating.
    Returns a list of dicts formatted similarly to our MatchScoreResult.
    """
    base_url = "https://huggingface.co/api/models"
    
    params = {
        "limit": 1000,
        "sort": "trendingScore",
        "direction": -1,
        "full": "False" # We just need basic metadata
    }
    
    all_results = []
    next_url = base_url
    
    try:
        # Loop up to 10 times to get 10,000 models
        for _ in range(10):
            if next_url == base_url:
                response = requests.get(next_url, params=params, timeout=15)
            else:
                response = requests.get(next_url, timeout=15)
                
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data:
                # Map HF metadata to our MatchScoreResult structure
                
                # Extract provider/author if available
                model_id = item.get("id", "")
                provider = model_id.split("/")[0] if "/" in model_id else "Community"
                name = model_id.split("/")[-1] if "/" in model_id else model_id
                
                # Find license from tags
                hf_tags_from_api = item.get("tags", [])
                license_val = "Open (Check HF Card)"
                for tag in hf_tags_from_api:
                    if tag.startswith("license:"):
                        license_val = tag.replace("license:", "").upper()
                        
                # Create a mock MatchScoreResult for UI compatibility
                mock_result = {
                    "is_hf_dynamic": True, # Flag to show HF badge
                    "model": {
                        "id": model_id,
                        "name": name,
                        "provider": provider,
                        "isModelOpenSource": True,
                        "licenseType": license_val,
                        "downloads": item.get("downloads", 0),
                        "likes": item.get("likes", 0),
                        "tags": hf_tags_from_api,
                        "createdAt": item.get("createdAt", "")
                    },
                    "overallScore": 85, # Default "good" score for trending models
                    "hardConstraintFailed": False,
                    "justification": {
                        "summary": "Dynamically fetched from Hugging Face Hub.",
                        "keyPros": [
                            f"{item.get('downloads', 0):,} recent downloads",
                            f"{item.get('likes', 0):,} community likes"
                        ],
                        "tradeOffs": ["Missing strict enterprise compliance guarantees", "Self-hosting required for data privacy"],
                        "governanceRationale": "Community-hosted weights. Review license for commercial use.",
                        "sovereigntyRationale": "Downloadable weights allow for 100% on-prem deployment."
                    }
                }
                results.append(mock_result)
                
            all_results.extend(results)
            
            # Check for next page
            link_header = response.headers.get("Link")
            if not link_header or 'rel="next"' not in link_header:
                break
                
            # Parse the next URL from the link header (e.g. '<https://...>; rel="next"')
            links = link_header.split(", ")
            next_link = [link for link in links if 'rel="next"' in link]
            if not next_link:
                break
                
            next_url = next_link[0].split(";")[0].strip("<>")
            
    except Exception as e:
        print(f"Error fetching from HF: {e}")
        
    return all_results


# --- scoring.py ---


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


# --- app.py ---






# --- Page Config ---
st.set_page_config(page_title="ModelMatch.AI ✨", page_icon="🤖", layout="wide")

# --- Custom Branding & Animation (HTML/CSS) ---
BRANDING_HTML = """
<style>
@keyframes pulseGlow {
  0% { filter: drop-shadow(0 0 2px #0056d6); }
  50% { filter: drop-shadow(0 0 10px #0056d6); transform: scale(1.02); }
  100% { filter: drop-shadow(0 0 2px #0056d6); }
}
.animated-svg {
  animation: pulseGlow 3s infinite alternate ease-in-out;
}
.header-container {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0 25px 0;
    border-bottom: 2px solid rgba(255,255,255,0.1);
    margin-bottom: 25px;
}
.brand-text-container {
    display: flex;
    flex-direction: column;
}
.app-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    background: -webkit-linear-gradient(45deg, #4F46E5, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.ntt-data-sub {
    font-size: 0.9rem;
    font-weight: 600;
    color: #8892b0;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 5px;
}
.hf-badge {
    background-color: #fbbf24;
    color: #000;
    font-size: 0.7rem;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 8px;
    display: inline-block;
}
</style>
<div class="header-container">
    <svg width="60" height="60" viewBox="0 0 100 100" class="animated-svg">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#4F46E5" stroke-width="4" stroke-dasharray="10 5" />
        <circle cx="50" cy="50" r="30" fill="none" stroke="#06b6d4" stroke-width="3" />
        <path d="M 50 20 L 80 50 L 50 80 L 20 50 Z" fill="#4F46E5" opacity="0.8" />
        <circle cx="50" cy="50" r="10" fill="#fff" />
    </svg>
    <div class="brand-text-container">
        <h1 class="app-title">ModelMatch.AI ✨</h1>
        <div class="ntt-data-sub">NTT DATA CTO Team of CGO Office</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Data current as of July 2026</div>
    </div>
</div>
"""
st.markdown(BRANDING_HTML, unsafe_allow_html=True)

# --- Load Database ---
@st.cache_data
def load_db():
    return CURATED_MODELS_DB

@st.cache_data(ttl=86400, show_spinner=False)
def load_hf_top_10000():
    
    return fetch_top_10000_models()

models_db = load_db()
all_hf_models = load_hf_top_10000()

# --- Sidebar Inputs (Form) ---
if st.sidebar.button("🗑️ Clear All Filters", use_container_width=True):
    st.session_state.clear()
    st.rerun()

with st.sidebar.form("criteria_form"):
    st.markdown("### ⚙️ Filter Models")
    

    with st.expander("1. Geography & Sovereignty"):
        region = st.selectbox("Deployment Region", ["US", "EU", "APAC", "MiddleEast", "LatAm", "Global"])
        data_sov = st.selectbox("Data Sovereignty Level", ["standard_cloud", "regional_boundary", "dedicated_vpc", "air_gapped_on_prem"])
        cross_border = st.checkbox("Strict Cross-Border Prohibition")

    with st.expander("2. Enterprise Governance (Strict)"):
        st.caption("Checking these disables dynamic Hugging Face fetching.")
        hipaa = st.checkbox("HIPAA (Health Data)")
        fedramp = st.selectbox("FedRAMP Level", ["none", "moderate", "high"])
        eu_ai_act = st.selectbox("EU AI Act Compliance", ["none", "gpai_standard", "high_risk_system"])
        gdpr = st.checkbox("GDPR Strict (Zero Training)")
        soc2 = st.checkbox("SOC 2 / ISO 27001")
        nist = st.checkbox("NIST AI RMF Alignment")

    with st.expander("3. Domain & Enterprise Task"):
        domain = st.selectbox("Industry Domain", ["general", "software", "healthcare", "finance", "legal", "ecommerce", "defense", "research", "education"])
        task_type = st.selectbox("Primary Task Type", ["chat", "code", "reasoning", "rag_longdoc", "data_extraction", "agentic_workflow", "creative_writing"])
        multi_vision = st.checkbox("Multimodal: Vision (Images)")
        multi_audio = st.checkbox("Multimodal: Audio (Speech)")
        context_window = st.selectbox("Minimum Context Window", ["small_8k", "medium_32k", "large_128k", "ultra_1m"])

    with st.expander("4. Technical Constraints"):
        latency = st.selectbox("Latency SLA", ["standard_batch", "fast_1s", "realtime_200ms"])
        structured_out = st.selectbox("Structured Output", ["none", "json_mode", "function_calling"])
        deployment_arch = st.selectbox("Deployment Architecture", ["saas_api", "private_cloud_vpc", "on_prem_gpu", "edge_mobile"])
        vendor_pref = st.selectbox("Vendor Preference", ["any", "openai", "anthropic", "google", "meta", "mistral", "deepseek", "cohere", "ibm"])
        license_req = st.selectbox("License Requirement", ["any", "open_weights", "open_source_apache"])

    with st.expander("5. Privacy & Budget"):
        data_retention = st.selectbox("Data Retention SLA", ["standard_30d", "zero_retention", "customer_managed_keys"])
        max_budget = st.number_input("Max Budget ($ / 1M Input Tokens)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
        est_in_tokens = st.number_input("Est. Monthly Input (M Tokens)", min_value=0, max_value=10000, value=10)
        est_out_tokens = st.number_input("Est. Monthly Output (M Tokens)", min_value=0, max_value=10000, value=2)

    with st.expander("🤗 Hugging Face Community Filters", expanded=True):
        st.caption("Granular taxonomy for dynamic model discovery. Ignored if strict enterprise governance is active.")
        
        hf_sort = st.selectbox("Sort Live Models By", ["Trending (Hot)", "Latest (Newest First)", "Most Downloaded", "Most Liked"])
        hf_limit = st.slider("Max HF Models to Display", min_value=1, max_value=10000, value=50, step=10)
        
        hf_nlp_tasks = st.multiselect("NLP Tasks", ["text-generation", "text-classification", "token-classification", "question-answering", "summarization", "translation"])
        hf_cv_tasks = st.multiselect("Vision Tasks", ["image-classification", "image-to-text", "text-to-image", "object-detection", "image-segmentation"])
        hf_audio_tasks = st.multiselect("Audio Tasks", ["text-to-speech", "automatic-speech-recognition", "audio-classification", "voice-activity-detection"])
        hf_mm_tasks = st.multiselect("Multimodal / Other", ["feature-extraction", "document-question-answering", "visual-question-answering", "reinforcement-learning", "tabular-classification"])
        
        hf_libraries = st.multiselect("Libraries", ["pytorch", "safetensors", "transformers", "gguf", "jax", "tensorflow", "onnx", "coreml", "keras"])
        hf_languages = st.multiselect("Languages", ["en", "fr", "de", "es", "zh", "ja", "ru", "hi", "it", "pt", "ko"])
        hf_licenses = st.multiselect("Licenses", ["mit", "apache-2.0", "openrail", "llama2", "llama3", "creativeml-openrail-m", "gpl-3.0", "bsd", "cc-by-4.0", "cc-by-nc-4.0"])

    # Submit Button
    submitted = st.form_submit_button("🚀 Apply Filters", use_container_width=True)

# Build criteria dict from the current widget states (for enterprise scoring)
criteria = {
    "region": region,
    "dataSovereignty": data_sov,
    "crossBorderProhibited": cross_border,
    "hipaa": hipaa,
    "fedramp": fedramp,
    "euAiAct": eu_ai_act,
    "gdpr": gdpr,
    "soc2Iso": soc2,
    "nistRmf": nist,
    "domain": domain,
    "taskType": task_type,
    "multimodalVision": multi_vision,
    "multimodalAudio": multi_audio,
    "contextWindow": context_window,
    "latency": latency,
    "structuredOutput": structured_out,
    "deploymentArchitecture": deployment_arch,
    "vendorPreference": vendor_pref,
    "licenseRequirement": license_req,
    "dataRetentionSla": data_retention,
    "maxBudgetPerMillion": max_budget,
    "estimatedMonthlyInputTokensM": est_in_tokens,
    "estimatedMonthlyOutputTokensM": est_out_tokens
}

# Top Search Bar (Live Search - outside the form)
st.caption("🟢 Live Search")
search_query = st.text_input("🔍 Search Models by Name or Provider...", placeholder="e.g. Llama 3, GPT-4, Mistral", label_visibility="collapsed")

# --- Hybrid Scoring & Fetching ---
# 1. Curated Models
all_results = rank_llms_for_inputs(models_db, criteria)
if search_query:
    all_results = [r for r in all_results if search_query.lower() in r['model']['name'].lower() or search_query.lower() in r['model']['provider'].lower()]

top_results = all_results[:5]

# 2. Dynamic Hugging Face Models
# Check if strict enterprise filters are enabled. If they are, we DON'T fetch from HF.
strict_enterprise_enabled = (hipaa or fedramp != "none" or eu_ai_act != "none" or gdpr or soc2 or nist)

# Also disable HF fetch if they explicitly want a SaaS API (HF models are weights for self-hosting)
if deployment_arch == "saas_api":
    strict_enterprise_enabled = True

if not strict_enterprise_enabled:
    with st.spinner("Fetching dynamic models from Hugging Face..."):
        
        # Compile HF tags from UI
        compiled_hf_tags = []
        compiled_hf_tags.extend(hf_nlp_tasks)
        compiled_hf_tags.extend(hf_cv_tasks)
        compiled_hf_tags.extend(hf_audio_tasks)
        compiled_hf_tags.extend(hf_mm_tasks)
        compiled_hf_tags.extend(hf_libraries)
        compiled_hf_tags.extend(hf_languages)
        compiled_hf_tags.extend([f"license:{lic}" for lic in hf_licenses])
        
        # Map general enterprise filters to HF tags to ensure accurate fetching
        if task_type == "chat" and "text-generation" not in compiled_hf_tags:
            compiled_hf_tags.append("text-generation")
        if multi_vision and "image-to-text" not in compiled_hf_tags:
            compiled_hf_tags.append("image-to-text")
        if multi_audio and "automatic-speech-recognition" not in compiled_hf_tags:
            compiled_hf_tags.append("automatic-speech-recognition")
        if license_req == "open_source_apache" and "license:apache-2.0" not in compiled_hf_tags:
            compiled_hf_tags.append("license:apache-2.0")
            
        # Map HF Sort Option
        hf_sort_map = {
            "Trending (Hot)": "trendingScore",
            "Latest (Newest First)": "createdAt",
            "Most Downloaded": "downloads",
            "Most Liked": "likes"
        }
        api_sort_val = hf_sort_map.get(hf_sort, "trendingScore")
            
        # Local Filtering Algorithm
        filtered_hf = all_hf_models
        
        # 1. Filter by Vendor Preference
        if vendor_pref != "any":
            filtered_hf = [m for m in filtered_hf if vendor_pref.lower() in m['model']['provider'].lower() or vendor_pref.lower() in m['model']['name'].lower()]
            
        # 2. Filter by Live Search Query
        if search_query:
            sq = search_query.lower()
            filtered_hf = [m for m in filtered_hf if sq in m['model']['name'].lower() or sq in m['model']['provider'].lower()]
            
        # 3. Filter by Exact HF Tags (Requires ALL selected tags)
        if compiled_hf_tags:
            for tag in compiled_hf_tags:
                filtered_hf = [m for m in filtered_hf if tag in m['model'].get('tags', [])]
                
        # 4. Sort Locally
        if api_sort_val == "downloads":
            filtered_hf.sort(key=lambda x: x['model'].get('downloads', 0), reverse=True)
        elif api_sort_val == "likes":
            filtered_hf.sort(key=lambda x: x['model'].get('likes', 0), reverse=True)
        elif api_sort_val == "createdAt":
            filtered_hf.sort(key=lambda x: x['model'].get('createdAt', ""), reverse=True)
        # For 'trendingScore', the original list is already sorted by trending.
            
        hf_models = filtered_hf[:hf_limit]
        
        if hf_models:
            # Append HF models to our top results, then resort
            top_results.extend(hf_models)
            top_results.sort(key=lambda x: x['overallScore'], reverse=True)
            # We don't slice top_results here anymore because the user wants to see up to 10,000 in the table.

if not top_results or (top_results[0].get('overallScore', 0) == 0 and not top_results[0].get('is_hf_dynamic')):
    st.warning("No models match your current search & strict filters.")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Model Grid", "📊 Data Table", "📈 Dynamic Reports", "⚖️ Compare Models", "🗄️ Full Database"])

    with tab1:
        grid_results = top_results
        if len(top_results) > 100:
            st.info(f"⚡ Grid view is capped at 100 models to prevent browser lag. View all {len(top_results)} results in the **Data Table** tab.")
            grid_results = top_results[:100]
            
        # Create a 2-column grid layout for cards
        cols = st.columns(2)
        for i, res in enumerate(grid_results):
            model = res['model']
            score_color = "green" if res.get('overallScore', 0) >= 80 else ("orange" if res.get('overallScore', 0) >= 50 else "red")
            is_hf = res.get('is_hf_dynamic', False)
            
            # Place in left or right column
            col = cols[i % 2]
            
            with col:
                with st.container(border=True):
                    # Title line with optional HF badge
                    title_html = f"<h4>{i+1}. {model['name']}"
                    if is_hf:
                        title_html += "<span class='hf-badge'>🤗 Hugging Face</span>"
                    title_html += "</h4>"
                    st.markdown(title_html, unsafe_allow_html=True)
                    
                    access_type = "🔓 Open Source" if model.get('isModelOpenSource') else "🔒 Proprietary API"
                    st.markdown(f"**Provider:** {model['provider']} | **License:** {model.get('licenseType', 'N/A')} ({access_type}) | **Overall Match:** :{score_color}[{res.get('overallScore', 0)}%]")
                    
                    if not is_hf:
                        if res.get('hardConstraintFailed'):
                            st.error("⚠️ Failed Hard Constraints")
                            for reason in res.get('hardConstraintReasons', []):
                                st.write(f"- {reason}")
                        else:
                            st.success("✅ Passes All Hard Constraints")
                    else:
                        st.info(f"⬇️ {model.get('downloads', 0):,} Downloads | ❤️ {model.get('likes', 0):,} Likes")
                    
                    st.write(res['justification']['summary'])
                    
                    if not is_hf:
                        st.markdown("---")
                        st.markdown(f"**Governance Rationale:** {res['justification']['governanceRationale']}")
                        st.markdown(f"**Sovereignty Rationale:** {res['justification']['sovereigntyRationale']}")
                        st.markdown(f"**Estimated Monthly Cost:** ${res.get('estimatedMonthlyCostUSD', 0):.2f}")

    with tab2:
        st.markdown("### 📊 Comprehensive Model Data")
        table_limit = st.slider("Number of models to show in table", min_value=1, max_value=len(top_results), value=len(top_results), key="table_limit_slider")
        
        table_data = []
        for i, res in enumerate(top_results[:table_limit]):
            model = res['model']
            is_hf = res.get('is_hf_dynamic', False)
            
            table_data.append({
                "Rank": i + 1,
                "Model": model['name'],
                "Provider": model['provider'],
                "Access Type": "Open Source" if model.get('isModelOpenSource') else "Closed",
                "License": model.get('licenseType', 'N/A'),
                "Release Date": model.get('releaseDate', 'N/A'),
                "Source": "Hugging Face Hub" if is_hf else "Curated DB",
                "Score": f"{res.get('overallScore', 0)}%",
                "Governance": "N/A (Community)" if is_hf else ("Fails" if res.get('hardConstraintFailed') else "Passes"),
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        # Only include non-HF models in the detailed reporting charts (since HF models lack detailed scoring breakdowns)
        curated_results = [r for r in top_results if not r.get('is_hf_dynamic')]
        
        if not curated_results:
            st.info("Dynamic reports are only available for curated enterprise models, not community Hugging Face models.")
        else:
            st.markdown("### Score Breakdown Analysis")
            breakdown_data = []
            for res in curated_results:
                breakdown_data.extend([
                    {"Model": res['model']['name'], "Category": "Compliance", "Score": res['complianceScore'] * 0.30},
                    {"Model": res['model']['name'], "Category": "Domain Fit", "Score": res['domainScore'] * 0.25},
                    {"Model": res['model']['name'], "Category": "Technical", "Score": res['technicalScore'] * 0.20},
                    {"Model": res['model']['name'], "Category": "Cost", "Score": res['costScore'] * 0.15},
                    {"Model": res['model']['name'], "Category": "Privacy", "Score": res['privacyScore'] * 0.10},
                ])
                
            df_breakdown = pd.DataFrame(breakdown_data)
            
            stacked_bar = alt.Chart(df_breakdown).mark_bar().encode(
                x=alt.X('sum(Score):Q', title='Weighted Score Contribution'),
                y=alt.Y('Model:N', sort=alt.EncodingSortField(field="Score", op="sum", order="descending")),
                color=alt.Color('Category:N', scale=alt.Scale(scheme='tableau10')),
                tooltip=['Model', 'Category', 'Score']
            ).properties(height=300)
            
            st.altair_chart(stacked_bar, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Cost vs. Latency Sweet Spot")
            scatter_data = []
            for res in curated_results:
                scatter_data.append({
                    "Model": res['model']['name'],
                    "Cost ($/1M Input)": res['model'].get('inputCostPerM', 0),
                    "Latency (ms)": res['model'].get('latencyAvgMs', 0),
                    "Overall Score": res['overallScore']
                })
                
            df_scatter = pd.DataFrame(scatter_data)
            
            scatter_plot = alt.Chart(df_scatter).mark_circle().encode(
                x=alt.X('Cost ($/1M Input):Q', title='Cost ($/1M Input Tokens)'),
                y=alt.Y('Latency (ms):Q', title='Latency (ms)', scale=alt.Scale(reverse=True)), 
                size=alt.Size('Overall Score:Q', scale=alt.Scale(range=[100, 1000]), legend=None),
                color=alt.Color('Overall Score:Q', scale=alt.Scale(scheme='viridis')),
                tooltip=['Model', 'Cost ($/1M Input)', 'Latency (ms)', 'Overall Score']
            ).properties(height=400)
            
            text_labels = scatter_plot.mark_text(
                align='left',
                baseline='middle',
                dx=15
            ).encode(
                text='Model:N'
            )
            
            st.altair_chart(scatter_plot + text_labels, use_container_width=True)

    with tab4:
        st.markdown("### Side-by-Side Model Comparison")
        model_options = {f"{r['model']['name']} ({r['model']['provider']})": r for r in top_results}
        selected_models = st.multiselect(
            "Select up to 4 models to compare:", 
            list(model_options.keys()), 
            default=list(model_options.keys())[:2] if len(model_options) >= 2 else list(model_options.keys()),
            max_selections=4
        )
        
        if selected_models:
            comp_cols = st.columns(len(selected_models))
            for i, sm in enumerate(selected_models):
                r = model_options[sm]
                m = r['model']
                is_hf = r.get('is_hf_dynamic', False)
                with comp_cols[i]:
                    with st.container(border=True):
                        st.markdown(f"#### {m['name']}")
                        st.markdown(f"**Score:** {r.get('overallScore', 0)}%")
                        st.markdown(f"**Provider:** {m['provider']}")
                        st.markdown(f"**Release Date:** {m.get('releaseDate', 'N/A')}")
                        st.markdown(f"**License:** {m.get('licenseType', 'N/A')}")
                        st.markdown("---")
                        if not is_hf:
                            st.markdown(f"**Context:** {m.get('contextWindow', 'N/A')}")
                            st.markdown(f"**Latency:** {m.get('latencyAvgMs', 'N/A')} ms")
                            st.markdown(f"**Input Cost/M:** ${m.get('inputCostPerM', 0):.2f}")
                            st.markdown(f"**Output Cost/M:** ${m.get('outputCostPerM', 0):.2f}")
                        else:
                            st.markdown(f"**Downloads:** {m.get('downloads', 0):,}")
                            st.markdown(f"**Likes:** {m.get('likes', 0):,}")
                            st.markdown("*Community-hosted weights*")
                            
                        st.markdown("---")
                        st.caption(r['justification']['summary'])

    with tab5:
        st.markdown("### 🗄️ Unfiltered Full Database (10,000+ Models)")
        st.caption("This table contains the raw, unfiltered cache of all curated enterprise models and the top trending Hugging Face models.")
        
        db_limit = st.slider("Max rows to render", min_value=1, max_value=len(models_db) + len(all_hf_models), value=min(1000, len(models_db) + len(all_hf_models)), key="db_slider")
        
        raw_table_data = []
        
        # Add curated models
        for m in models_db:
            raw_table_data.append({
                "Model": m.get('name', 'N/A'),
                "Provider": m.get('provider', 'N/A'),
                "Source": "Curated Enterprise DB",
                "Downloads": "N/A",
                "Likes": "N/A",
                "Created At": m.get('releaseDate', 'N/A'),
                "Tags": ", ".join(m.get('taskType', []) if isinstance(m.get('taskType', []), list) else []),
                "License": m.get('licenseType', 'N/A'),
                "Context Window": m.get('contextWindow', 'N/A'),
                "Latency (ms)": m.get('latencyAvgMs', 'N/A'),
                "Input Cost ($/M)": m.get('inputCostPerM', 'N/A'),
                "Output Cost ($/M)": m.get('outputCostPerM', 'N/A'),
                "Vision": "Yes" if m.get('taskCapabilities', {}).get('vision') else "No",
                "Audio": "Yes" if m.get('taskCapabilities', {}).get('audio') else "No",
                "Regions": ", ".join(m.get('compliance', {}).get('regionsSupported', [])),
                "HIPAA": "Yes" if m.get('compliance', {}).get('hipaaBaa') else "No",
                "FedRAMP": m.get('compliance', {}).get('fedrampStatus', 'N/A'),
                "EU AI Act": m.get('compliance', {}).get('euAiActCompliance', 'N/A'),
                "GDPR": m.get('compliance', {}).get('gdprDataTraining', 'N/A'),
                "SOC 2 / ISO": "Yes" if m.get('compliance', {}).get('soc2IsoCert') else "No",
                "NIST RMF": "Yes" if m.get('compliance', {}).get('nistRmfCompliant') else "No"
            })
            
        # Add HF models
        for item in all_hf_models:
            m = item['model']
            raw_table_data.append({
                "Model": str(m.get('name', 'N/A')),
                "Provider": str(m.get('provider', 'N/A')),
                "Source": "Hugging Face Hub",
                "Downloads": str(m.get('downloads', 0)),
                "Likes": str(m.get('likes', 0)),
                "Created At": str(m.get('createdAt', 'N/A')[:10] if m.get('createdAt') else 'N/A'),
                "Tags": str(", ".join(m.get('tags', [])[:5]) + ("..." if len(m.get('tags', [])) > 5 else "")),
                "License": str(m.get('licenseType', 'N/A')),
                "Context Window": "N/A",
                "Latency (ms)": "N/A",
                "Input Cost ($/M)": "N/A",
                "Output Cost ($/M)": "N/A",
                "Vision": "Yes" if "image-to-text" in m.get('tags', []) else "No/Unknown",
                "Audio": "Yes" if "automatic-speech-recognition" in m.get('tags', []) else "No/Unknown",
                "Regions": "Global (Open Weights)",
                "HIPAA": "N/A",
                "FedRAMP": "N/A",
                "EU AI Act": "N/A",
                "GDPR": "N/A",
                "SOC 2 / ISO": "N/A",
                "NIST RMF": "N/A"
            })
            
        df_raw = pd.DataFrame(raw_table_data)
        # Convert all columns to strings to prevent PyArrow ArrowTypeError from mixed types
        df_raw = df_raw.astype(str)
        st.dataframe(df_raw.head(db_limit), use_container_width=True, hide_index=True)
