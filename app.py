import streamlit as st
import json
import pandas as pd
import altair as alt
from scoring import rank_llms_for_inputs


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
    with open('db.json', 'r') as f:
        return json.load(f)

@st.cache_data(ttl=86400, show_spinner=False)
def load_hf_top_10000():
    from hf_api import fetch_top_10000_models
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
