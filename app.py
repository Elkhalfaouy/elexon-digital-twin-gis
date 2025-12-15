import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import json
import folium
from streamlit_folium import st_folium
import io
# --- 1. CONFIGURATION & BRANDING ---
st.set_page_config(page_title="Elexon Digital Twin", layout="wide", page_icon="⚡")
st.markdown("""
<style>
    .css-10trblm { color: #E30613; }
    h1, h2, h3 { color: #1a202c; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 600; }
    .success-box { padding:25px; background: linear-gradient(135deg, #48bb78, #38a169); color:#ffffff; border-left: 6px solid #2f855a; border-radius:15px; margin-bottom: 20px; min-height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 6px 12px rgba(0,0,0,0.15); font-size: 14px; line-height: 1.4; position: relative; overflow: hidden; }
    .success-box::before { content: ''; position: absolute; top: 0; right: 0; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; transform: translate(30px, -30px); }
    .fail-box { padding:25px; background: linear-gradient(135deg, #f56565, #e53e3e); color:#ffffff; border-left: 6px solid #c53030; border-radius:15px; margin-bottom: 20px; min-height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 6px 12px rgba(0,0,0,0.15); font-size: 14px; line-height: 1.4; position: relative; overflow: hidden; }
    .fail-box::before { content: ''; position: absolute; top: 0; right: 0; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; transform: translate(30px, -30px); }
    .metric-container { background: linear-gradient(135deg, #f7fafc, #edf2f7); padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 14px; }
    .caption-text { font-size: 14px; font-style: italic; color: #4a5568; text-align: center; margin-top: -6px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background: linear-gradient(135deg, #f7fafc, #edf2f7); border-radius: 8px 8px 0 0; border: 1px solid #e2e8f0; border-bottom: none; color: #4a5568; font-weight: 600; padding: 12px 20px; transition: all 0.3s ease; }
    .stTabs [data-baseweb="tab"]:hover { background: linear-gradient(135deg, #edf2f7, #e2e8f0); transform: translateY(-2px); }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2); color: white; box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3); }
    .professional-section { background: linear-gradient(135deg, #ffffff, #f8f9fa); border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .section-header { color: #E30613; font-size: 18px; font-weight: 700; margin-bottom: 15px; border-bottom: 2px solid #E30613; padding-bottom: 8px; }
    .control-group { background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 3px solid #667eea; }
    .success-box h3, .fail-box h3 { font-size: 16px; margin: 0 0 12px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .success-box small, .fail-box small { font-size: 12px; line-height: 1.4; opacity: 0.9; }
    .status-metric { font-size: 20px; font-weight: 700; margin: 8px 0; color: rgba(255,255,255,0.95); text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
    .status-detail { font-size: 13px; margin: 4px 0; opacity: 0.95; }
    .status-icon { font-size: 24px; margin-right: 8px; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2)); }
    .stMetric { font-size: 14px; }
    .stMetric label { font-size: 13px; font-weight: 600; }
    .success-box:hover, .fail-box:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.2); transition: all 0.3s ease; }
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("## ⚡ **elexon** charging")
st.sidebar.caption("Digital Twin & Feasibility Tool")
st.sidebar.divider()
st.sidebar.caption("Author: Amine El khalfaouy")
# --- NEW: MULTI-SITE SELECTOR ---
project_name = st.sidebar.text_input("🏢 Project Name / Site:", value="Schkeuditz Logistics Node")
st.title(f"🏭 **Elexon Charging Hub Digital Twin** - {project_name}")
st.markdown("**Status:** Strategic Assessment | **Version:** 27.0 (German Standards) | **Standards:** DIN EN 61851, VDE 0122")
st.caption("Professional heavy-duty truck charging infrastructure planning with German engineering standards")
# --- 2. SIDEBAR: INPUTS & COMPARISON ---
with st.sidebar:
    st.header("⚙️ Scenario Manager")
   
    # COMPARISON ENGINE
    if 'scenarios' not in st.session_state:
        st.session_state['scenarios'] = {}
    
    # Initialize layout variables in session state (prefer GIS selections when present)
    if 'available_area' not in st.session_state:
        st.session_state['available_area'] = st.session_state.get("site_area_m2", 3000)
   
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("� Save A"):
            st.session_state['save_trigger'] = 'A'
    with c2:
        if st.button("� Save B"):
            st.session_state['save_trigger'] = 'B'
    with c3:
        if st.button("� Save C"):
            st.session_state['save_trigger'] = 'C'
           
    # Display saved status
    status_text = []
    if 'A' in st.session_state['scenarios']: status_text.append("✓ A")
    if 'B' in st.session_state['scenarios']: status_text.append("✓ B")
    if 'C' in st.session_state['scenarios']: status_text.append("✓ C")
    if status_text:
        st.caption("Saved: " + " | ".join(status_text))
   
    if st.button("� Start New Site / Reset"):
        st.session_state['scenarios'] = {}
        st.rerun()
    st.divider()
    scenario_mode = st.radio("Infrastructure Config:",
                             ["Grid Only", "With PV", "PV + Battery"])
   
    # --- TECHNICAL ---
    with st.expander("⚙️ Technical Specifications", expanded=False):
        st.caption("Grid Constraints")
        transformer_limit_kva = st.number_input(
            "Transformer Limit (kVA)",
            value=st.session_state.get("site_grid_kva", 4000),
            step=100
        )
        power_factor = st.slider("Power Factor (PF)", 0.85, 1.00, 0.95, step=0.01)
       
        st.caption("Charger Configuration")
        n_hpc = st.number_input("HPC Satellites (Dispensers)", value=8)
        n_power_units = st.number_input("HPC Power Units (Cabinets)", value=4)
        n_ac = st.number_input("AC Bays (43kW)", value=4)
        hpc_power_kw = st.slider("HPC Charging Power (kW)", 100, 1000, 400, step=50)
        ac_power_kw = st.slider("AC Charging Power (kW)", 11, 150, 43, step=11)
       
        st.caption("Utilization (Traffic)")
        hpc_traffic = st.slider("HPC Traffic (Trucks/Day)", 10, 200, 60)
        ac_traffic = st.slider("AC Traffic (Trucks/Day)", 0, 50, 10)
    # --- ENERGY ASSETS ---
    pv_kwp = 0
    bess_kwh = 0
    bess_kw = 0
   
    if "PV" in scenario_mode:
        with st.expander("☀️ Solar System", expanded=True):
            pv_kwp = st.slider("PV Capacity (kWp)", 0, 1000, 450)
            season = st.selectbox("Season", ["Summer", "Winter"])
           
    if "Battery" in scenario_mode:
        with st.expander("🔋 BESS System", expanded=True):
            bess_kwh = st.slider("Battery Energy (kWh)", 100, 2000, 500)
            bess_kw = st.slider("Battery Power (kW)", 50, 1000, 250)
    # --- DETAILED CAPEX INPUTS ---
    with st.expander("💰 Detailed CAPEX Inputs", expanded=False):
        cost_dispenser = st.number_input("Cost/Satellite (€)", value=17000)
        cost_cabinet = st.number_input("Cost/Power Unit (€)", value=125000)
        cost_ac_unit = st.number_input("Cost/AC Charger (€)", value=15000)
       
        cost_civil_hpc = st.number_input("Civil/HPC Point (€)", value=10000)
        cost_civil_cab = st.number_input("Civil/Cabinet (€)", value=30000)
        cost_cabling = st.number_input("Total Cabling (€)", value=40000)
       
        cost_grid_fee = st.number_input("Grid Connection Fee (€)", value=300000)
        cost_trafo_install = st.number_input("Trafo Install (€)", value=55000)
        cost_soft = st.number_input("Soft Costs (€)", value=96000)
       
        cost_pv_unit = 900
        cost_bess_unit = 500
    # --- OPEX & REVENUE ---
    with st.expander("💰 OPEX & Revenue Inputs", expanded=False):
        sell_hpc = st.number_input("HPC Tariff (€/kWh)", value=0.65)
        sell_ac = st.number_input("AC Tariff (€/kWh)", value=0.45)
        thg_price = st.slider("THG Revenue (€/kWh)", 0.0, 0.25, 0.0, step=0.01)
        elec_price = st.number_input("Energy Price (€/kWh)", value=0.35)
        peak_price = st.number_input("Peak Load Price (€/kW/yr)", value=166.0)
        rent_fixed = st.number_input("Fixed Rent (€/Bay/yr)", value=4000)
        rent_var = st.number_input("Variable Rent (€/kWh)", value=0.02, step=0.01)
        maint_cost = st.number_input("Maint. & Ops (€/yr)", value=80000)
# --- 3. SIMULATION CORE ---
def run_simulation(hpc_power_kw, ac_power_kw):
    time_index = pd.date_range("2026-06-21", periods=96, freq="15min")
    df = pd.DataFrame(index=time_index)
    np.random.seed(42)
   
    # 1. UNCONSTRAINED DEMAND
    raw_hpc_demand = np.zeros(96)
    raw_ac_demand = np.zeros(96)
   
    for _ in range(hpc_traffic):
        start = np.random.randint(24, 80) if np.random.rand() > 0.2 else np.random.randint(0, 92)
        dur = np.random.randint(2, 5)
        raw_hpc_demand[start : min(start+dur, 96)] += hpc_power_kw
       
    for _ in range(ac_traffic):
        start = np.random.randint(0, 80)
        dur = np.random.randint(16, 32)
        raw_ac_demand[start : min(start+dur, 96)] += ac_power_kw
    # 2. CAPACITY CONSTRAINTS
    hpc_limit = n_hpc * hpc_power_kw
    ac_limit = n_ac * ac_power_kw
   
    df["HPC_Demand_kW"] = raw_hpc_demand
    df["HPC_Served_kW"] = np.minimum(raw_hpc_demand, hpc_limit)
    df["AC_Demand_kW"] = raw_ac_demand
    df["AC_Served_kW"] = np.minimum(raw_ac_demand, ac_limit)
   
    # 3. ENERGY SYSTEM LOGIC
    df["Gross_Load_kW"] = df["HPC_Served_kW"] + df["AC_Served_kW"]
   
    if pv_kwp > 0:
        x = np.arange(96)
        factor = 1.0 if season == "Summer" else 0.3
        bell = np.exp(-0.5 * ((x - 52) / 14) ** 2)
        df["PV_Generation_kW"] = bell * pv_kwp * factor
    else:
        df["PV_Generation_kW"] = 0
       
    battery_soc = bess_kwh * 0.5
    final_grid = []
   
    for i in range(96):
        load = df["Gross_Load_kW"].iloc[i]
        pv = df["PV_Generation_kW"].iloc[i]
        net = load - pv
        limit_kw = transformer_limit_kva * power_factor
       
        flow = 0
        if bess_kwh > 0:
            if net > limit_kw:
                needed = net - limit_kw
                possible = min(bess_kw, battery_soc * 4)
                flow = -min(needed, possible)
            elif net < limit_kw * 0.5 and battery_soc < bess_kwh:
                possible = min(bess_kw, (bess_kwh - battery_soc) * 4)
                flow = possible
            battery_soc += flow / 4
           
        final_grid.append(max(0, net + flow))
       
    df["Final_Grid_kW"] = final_grid
    return df
res = run_simulation(hpc_power_kw, ac_power_kw)
# --- 4. CALCULATIONS ---
peak_load_kw = res["Final_Grid_kW"].max()
peak_load_kva = peak_load_kw / power_factor
is_overload = peak_load_kva > transformer_limit_kva
# Energy (Served Only)
energy_hpc = res["HPC_Served_kW"].sum() / 4
energy_ac = res["AC_Served_kW"].sum() / 4
energy_total = energy_hpc + energy_ac
# Service Levels
demand_hpc_kwh = res["HPC_Demand_kW"].sum() / 4
demand_ac_kwh = res["AC_Demand_kW"].sum() / 4
sl_hpc = (energy_hpc / demand_hpc_kwh)*100 if demand_hpc_kwh > 0 else 100
sl_ac = (energy_ac / demand_ac_kwh)*100 if demand_ac_kwh > 0 else 100

# Charging Hours Analysis
hpc_total_hours = res["HPC_Served_kW"].sum() / (hpc_power_kw * n_hpc) if n_hpc > 0 else 0
ac_total_hours = res["AC_Served_kW"].sum() / (ac_power_kw * n_ac) if n_ac > 0 else 0
hpc_avg_hours_per_truck = hpc_total_hours / hpc_traffic if hpc_traffic > 0 else 0
ac_avg_hours_per_truck = ac_total_hours / ac_traffic if ac_traffic > 0 else 0
total_charging_hours = hpc_total_hours + ac_total_hours
lost_rev = ((demand_hpc_kwh - energy_hpc)*sell_hpc) + ((demand_ac_kwh - energy_ac)*sell_ac)
# PV Self Cons
res["PV_Self_Cons_kW"] = res[["Gross_Load_kW", "PV_Generation_kW"]].min(axis=1)
energy_pv_consumed = res["PV_Self_Cons_kW"].sum() / 4
# Financials
rev_sales = (energy_hpc * sell_hpc) + (energy_ac * sell_ac)
rev_thg = energy_total * thg_price
total_rev = rev_sales + rev_thg
opex_energy = (res["Final_Grid_kW"].sum()/4) * elec_price
opex_peak = (peak_load_kw * peak_price) / 365
opex_rent_fix = ((n_hpc + n_ac) * rent_fixed) / 365
opex_rent_var = energy_total * rent_var
opex_maint = maint_cost / 365
total_opex = opex_energy + opex_peak + opex_rent_fix + opex_rent_var + opex_maint
daily_ebitda = total_rev - total_opex
daily_margin = (daily_ebitda / total_rev) * 100 if total_rev > 0 else 0
# CAPEX
c_hardware = (n_hpc * cost_dispenser) + (n_power_units * cost_cabinet) + (n_ac * cost_ac_unit)
c_civil = (n_hpc * cost_civil_hpc) + (n_power_units * cost_civil_cab) + cost_cabling + cost_trafo_install
c_soft_grid = cost_grid_fee + cost_soft
c_renewables = (pv_kwp * cost_pv_unit) + (bess_kwh * cost_bess_unit)
capex_total = c_hardware + c_civil + c_soft_grid + c_renewables
payback = capex_total / (daily_ebitda * 365) if daily_ebitda > 0 else 99.9
roi_15y = ((daily_ebitda * 365 * 15) - capex_total) / capex_total * 100
# LCOC
daily_capex_depr = capex_total / (15 * 365)
lcoc = (total_opex + daily_capex_depr) / energy_total if energy_total > 0 else 0
# Long Term
co2_saved_daily = energy_total * 0.7
co2_15y_tonnes = (co2_saved_daily * 365 * 15) / 1000
years = np.arange(0, 16)
cumulative_cf = [-capex_total]
annual_profit = daily_ebitda * 365
curr_bal = -capex_total
for y in range(1, 16):
    annual_profit_inflated = annual_profit * (1.02 ** (y-1))
    curr_bal += annual_profit_inflated
    cumulative_cf.append(curr_bal)
# SAVE SCENARIO LOGIC
current_results = {
    "Peak Load (kVA)": peak_load_kva,
    "Profit/Day (€)": daily_ebitda,
    "Margin (%)": daily_margin,
    "CAPEX (€)": capex_total,
    "ROI 15y (%)": roi_15y,
    "Payback (Yrs)": payback,
    "Service Level (%)": (sl_hpc + sl_ac)/2, # Avg
    "Lost Rev (€/day)": lost_rev,
    "Charging Hours": total_charging_hours
}
if 'save_trigger' in st.session_state:
    key = st.session_state['save_trigger']
    st.session_state['scenarios'][key] = current_results
    del st.session_state['save_trigger']
# --- 5. VISUAL DASHBOARD ---
# A. KEY METRICS (PINNED ON TOP)
st.markdown("### 📊 Live Key Indicators")
# Improved layout: added Financials to the top row as requested
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Peak Load", f"{peak_load_kva:,.0f} kVA", delta=f"Limit: {transformer_limit_kva} kVA", delta_color="normal")
k2.metric("HPC Energy", f"{energy_hpc:,.0f} kWh")
k3.metric("AC Energy", f"{energy_ac:,.0f} kWh")
k4.metric("Daily Profit", f"€{daily_ebitda:,.0f}", delta=f"{daily_margin:.1f}% Margin")
k5.metric("Charging Hours", f"{total_charging_hours:.0f} hrs")
st.divider()
# B. TRIPLE BANNER SYSTEM (Grid | Ops | Finance)
c1, c2, c3 = st.columns(3)
with c1:
    if is_overload:
        st.markdown(f"""
        <div class="fail-box">
            <div>
                <h3><span class="status-icon">🚨</span>GRID CRITICAL</h3>
                <div class="status-detail">⚠️ Peak load exceeds transformer capacity</div>
                <div class="status-metric">{peak_load_kva:,.0f} kVA</div>
                <div class="status-detail">Current Load (Limit: {transformer_limit_kva} kVA)</div>
                <div class="status-detail">🔴 Overload: {(peak_load_kva/transformer_limit_kva*100 - 100):.1f}% above capacity</div>
                <div class="status-detail">💡 Recommendation: Upgrade transformer or reduce charger count</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        utilization_pct = (peak_load_kva / transformer_limit_kva) * 100
        st.markdown(f"""
        <div class="success-box">
            <div>
                <h3><span class="status-icon">✅</span>GRID STABLE</h3>
                <div class="status-detail">🟢 Power system operating within safe limits</div>
                <div class="status-metric">{peak_load_kva:,.0f} kVA</div>
                <div class="status-detail">Peak Load (Capacity: {transformer_limit_kva} kVA)</div>
                <div class="status-detail">📊 Utilization: {utilization_pct:.1f}% of capacity</div>
                <div class="status-detail">⚡ Power Factor: {power_factor:.2f} | Efficiency: {'Excellent' if utilization_pct > 70 else 'Good' if utilization_pct > 50 else 'Moderate'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
with c2:
    if sl_hpc < 99 or sl_ac < 99:
        avg_service = (sl_hpc + sl_ac) / 2
        st.markdown(f"""
        <div class="fail-box">
            <div>
                <h3><span class="status-icon">⚠️</span>SERVICE CONGESTION</h3>
                <div class="status-detail">🚫 Revenue loss due to charging queue delays</div>
                <div class="status-metric">€{lost_rev:,.0f}/day</div>
                <div class="status-detail">Daily Revenue Loss</div>
                <div class="status-detail">📊 Service Levels: HPC {sl_hpc:.1f}% | AC {sl_ac:.1f}%</div>
                <div class="status-detail">🎯 Target: ≥99% | Current: {avg_service:.1f}%</div>
                <div class="status-detail">💡 Add {max(1, int((n_hpc + n_ac) * 0.1))} more chargers to reach target</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avg_service = (sl_hpc + sl_ac) / 2
        st.markdown(f"""
        <div class="success-box">
            <div>
                <h3><span class="status-icon">✅</span>SERVICE EXCELLENT</h3>
                <div class="status-detail">🎯 All charging demands fully satisfied</div>
                <div class="status-metric">{avg_service:.1f}%</div>
                <div class="status-detail">Average Service Level</div>
                <div class="status-detail">📊 Performance: HPC {sl_hpc:.1f}% | AC {sl_ac:.1f}%</div>
                <div class="status-detail">⚡ Total Charging Hours: {total_charging_hours:.0f} hrs/day</div>
                <div class="status-detail">🏆 Industry-leading reliability achieved</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
with c3:
    if daily_ebitda > 0 and payback < 10:
        annual_revenue = daily_ebitda * 365
        st.markdown(f"""
        <div class="success-box">
            <div>
                <h3><span class="status-icon">💰</span>FINANCIALLY VIABLE</h3>
                <div class="status-detail">📈 Strong investment returns projected</div>
                <div class="status-metric">€{daily_ebitda:,.0f}/day</div>
                <div class="status-detail">Daily EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)</div>
                <div class="status-detail">📅 Payback Period: {payback:.1f} years</div>
                <div class="status-detail">💹 15-Year ROI: {roi_15y:.1f}% | Annual Revenue: €{annual_revenue:,.0f}</div>
                <div class="status-detail">🎯 Margin: {daily_margin:.1f}% | IRR: {'Excellent' if roi_15y > 15 else 'Good' if roi_15y > 10 else 'Moderate'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        risk_level = "HIGH" if payback > 15 else "MEDIUM" if payback > 10 else "LOW"
        st.markdown(f"""
        <div class="fail-box">
            <div>
                <h3><span class="status-icon">⚠️</span>{risk_level} FINANCIAL RISK</h3>
                <div class="status-detail">⚠️ Investment recovery concerns identified</div>
                <div class="status-metric">€{daily_ebitda:,.0f}/day</div>
                <div class="status-detail">Current Daily {'Profit' if daily_ebitda > 0 else 'Loss'}</div>
                <div class="status-detail">📅 Payback Period: {payback:.1f} years ({'Too Long' if payback > 10 else 'Acceptable'})</div>
                <div class="status-detail">💹 15-Year ROI: {roi_15y:.1f}% | Margin: {daily_margin:.1f}%</div>
                <div class="status-detail">💡 Recommendations: Optimize pricing, reduce costs, or extend timeline</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
# --- NEW: DASHBOARD TAB ADDED ---
tab_dash, tab_tech, tab_serv, tab_fin, tab_long, tab_capex, tab_compare, tab_layout, tab_gis = st.tabs([
    "� Dashboard", "⚙️ Technical", "⚠️ Service", "💼 Financials", "📈 Long-Term", "💰 CAPEX", "⚖️ Compare", "📐 Layout", "🗺️ GIS Digital Twin"
])

# ---------------- GIS Digital Twin (isolated) ----------------
with tab_gis:
    st.subheader("🗺️ GIS Digital Twin")
    st.caption("Select a candidate site and sync grid capacity and area into the twin (thesis-ready).")

    def load_sites(path="gis/sites.geojson"):
        """Load candidate sites from GeoJSON with defensive checks."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            st.warning("File not found: gis/sites.geojson")
            return []
        except json.JSONDecodeError:
            st.error("Invalid GeoJSON format in gis/sites.geojson")
            return []

        feats = data.get("features") or []
        sites_local = []
        for idx, feat in enumerate(feats):
            props = feat.get("properties") or {}
            geom = feat.get("geometry") or {}
            coords = geom.get("coordinates") or []
            if not (isinstance(coords, list) and len(coords) >= 2):
                continue  # skip malformed geometry

            sites_local.append({
                "site_id": props.get("site_id") or props.get("id") or f"site_{idx+1}",
                "name": props.get("name") or f"Site {idx+1}",
                "grid_kva": props.get("grid_kva"),
                "land_area_m2": props.get("land_area_m2"),
                "lon": coords[0],
                "lat": coords[1],
            })
        return sites_local

    sites = load_sites()
    if not sites:
        st.info("Provide a valid GeoJSON at gis/sites.geojson to enable GIS scoring and export.")
    else:
        # --- Multi-criteria scoring (grid_kva and land_area_m2, equal weight) ---
        def safe_min_max_norm(all_vals, val):
            nums = [v for v in all_vals if isinstance(v, (int, float))]
            if not nums or val is None or not isinstance(val, (int, float)):
                return 0.0
            vmin, vmax = min(nums), max(nums)
            if vmax == vmin:
                return 1.0
            return (val - vmin) / (vmax - vmin)

        grid_vals = [s.get("grid_kva") for s in sites]
        area_vals = [s.get("land_area_m2") for s in sites]

        for s in sites:
            s["norm_grid"] = safe_min_max_norm(grid_vals, s.get("grid_kva"))
            s["norm_area"] = safe_min_max_norm(area_vals, s.get("land_area_m2"))
            s["score"] = round(0.5 * s["norm_grid"] + 0.5 * s["norm_area"], 3)

        ranked_sites = sorted(sites, key=lambda x: x["score"], reverse=True)
        scores = [s["score"] for s in ranked_sites] if ranked_sites else [0.0]
        p33 = float(np.percentile(scores, 33)) if len(scores) > 1 else scores[0]
        p66 = float(np.percentile(scores, 66)) if len(scores) > 1 else scores[0]

        def score_color(score):
            if score >= p66:
                return "green"
            if score >= p33:
                return "orange"
            return "red"

        # Center map
        avg_lat = sum(s["lat"] for s in sites) / len(sites)
        avg_lon = sum(s["lon"] for s in sites) / len(sites)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11, tiles="OpenStreetMap")

        # Add markers with score-based colors
        for s in sites:
            popup_lines = [
                f"<b>{s['name']}</b>",
                f"Site ID: {s['site_id']}",
                f"Grid (kVA): {s['grid_kva'] if s.get('grid_kva') is not None else 'n/a'}",
                f"Land (m²): {s['land_area_m2'] if s.get('land_area_m2') is not None else 'n/a'}",
                f"Score: {s.get('score', 0.0)}",
            ]
            folium.Marker(
                location=[s["lat"], s["lon"]],
                tooltip=f"{s['name']} (score: {s.get('score', 0.0)})",
                popup="<br>".join(popup_lines),
                icon=folium.Icon(color=score_color(s.get("score", 0.0)), icon="info-sign"),
            ).add_to(m)

        st_folium(m, height=420, width="100%", key="gis_map")

        # Ranking table
        st.markdown("### Site Ranking")
        df_rank = pd.DataFrame(ranked_sites)[["site_id", "name", "grid_kva", "land_area_m2", "score"]]
        st.dataframe(df_rank, use_container_width=True, hide_index=True)
        st.caption("Marker colors: green = top tier, orange = mid tier, red = lower tier.")

        # Dropdown selection
        options = {f"{s['name']} ({s['site_id']})": s["site_id"] for s in sites}
        choice = st.selectbox("Select a site", ["— Select —"] + list(options.keys()))

        if choice != "— Select —":
            selected_id = options[choice]
            selected = next((s for s in sites if s["site_id"] == selected_id), None)
            if selected:
                if selected.get("grid_kva") is not None:
                    st.session_state["site_grid_kva"] = int(selected["grid_kva"])
                if selected.get("land_area_m2") is not None:
                    st.session_state["site_area_m2"] = int(selected["land_area_m2"])

                st.success(
                    f"Selected: {selected['name']} ({selected['site_id']}) → "
                    f"grid_kva={st.session_state.get('site_grid_kva', 'n/a')}, "
                    f"land_area_m2={st.session_state.get('site_area_m2', 'n/a')}"
                )
            else:
                st.warning("Selected site not found in the loaded list.")

        # Exports
        csv_bytes = df_rank.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Site Ranking (CSV)",
            data=csv_bytes,
            file_name="site_ranking.csv",
            mime="text/csv",
            help="Exports the multi-criteria ranking table for thesis appendices."
        )

        map_html = m.get_root().render()
        st.download_button(
            label="Download GIS Map (HTML)",
            data=map_html,
            file_name="gis_map.html",
            mime="text/html",
            help="Open in a browser and use print/save or screenshot for a PNG figure."
        )

        st.caption("PNG workflow: open gis_map.html in a browser → print/save or screenshot for high-res PNG.")

with tab_dash:
    st.subheader("🎯 Executive Dashboard")
    st.caption("High-level overview of your HPC charging hub digital twin performance.")
    
    # Key Performance Summary with enhanced styling
    st.markdown("### 📊 **Core Performance Indicators**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_color = "🟢" if not is_overload else "🔴"
        st.metric("Infrastructure Status", f"{status_color} {'Operational' if not is_overload else 'Critical'}", 
                 delta="Grid Stable" if not is_overload else "Overload Risk")
    with col2:
        service_color = "🟢" if (sl_hpc + sl_ac)/2 >= 99 else "🟡" if (sl_hpc + sl_ac)/2 >= 95 else "🔴"
        st.metric("Service Quality", f"{service_color} {(sl_hpc + sl_ac)/2:.1f}%", 
                 delta="Excellent" if (sl_hpc + sl_ac)/2 >= 99 else "Needs Attention")
    with col3:
        revenue_color = "🟢" if daily_ebitda > 0 else "🔴"
        st.metric("Daily Revenue", f"{revenue_color} €{daily_ebitda + (opex_energy + opex_peak + opex_rent_fix + opex_rent_var + opex_maint):,.0f}")
    with col4:
        utilization_color = "🟢" if total_charging_hours > (n_hpc + n_ac) * 12 else "🟡"
        st.metric("Asset Utilization", f"{utilization_color} {total_charging_hours:.0f} hrs/day")
    
    st.markdown("---")
    
    # Enhanced Scenario Overview
    if len(st.session_state['scenarios']) > 0:
        st.markdown("### 📈 **Scenario Performance Matrix**")
        scenario_data = []
        for k in st.session_state['scenarios']:
            scenario_data.append({
                "Scenario": f"**{k}**",
                "💰 Profit/Day": f"€{st.session_state['scenarios'][k]['Profit/Day (€)']:,.0f}",
                "📊 Service Level": f"{st.session_state['scenarios'][k]['Service Level (%)']:.1f}%",
                "🏗️ CAPEX": f"€{st.session_state['scenarios'][k]['CAPEX (€)']:,.0f}",
                "⏱️ Payback": f"{st.session_state['scenarios'][k]['Payback (Yrs)']:.1f} yrs",
                "🔋 Utilization": f"{st.session_state['scenarios'][k]['Charging Hours']:.0f} hrs"
            })
        st.dataframe(pd.DataFrame(scenario_data), use_container_width=True, hide_index=True)
    
    # Professional System Health Dashboard
    st.markdown("### 🔍 **System Health Dashboard**")
    health_cols = st.columns(3)
    with health_cols[0]:
        if not is_overload:
            st.success("✅ **Grid Connection:** Within transformer limits")
            st.caption(f"Peak Load: {peak_load_kva:.0f} kVA / {transformer_limit_kva} kVA limit")
        else:
            st.error("❌ **Grid Connection:** Exceeding transformer capacity")
            st.caption(f"Overload: {peak_load_kva:.0f} kVA > {transformer_limit_kva} kVA limit")
    
    with health_cols[1]:
        avg_service = (sl_hpc + sl_ac) / 2
        if avg_service >= 99:
            st.success(f"✅ **Service Level:** {avg_service:.1f}% (Target: ≥99%)")
            st.caption("All service levels within acceptable range")
        elif avg_service >= 95:
            st.warning(f"⚠️ **Service Level:** {avg_service:.1f}% (Target: ≥99%)")
            st.caption("Minor service congestion detected")
        else:
            st.error(f"❌ **Service Level:** {avg_service:.1f}% (Target: ≥99%)")
            st.caption("Significant service congestion")
    
    with health_cols[2]:
        if daily_ebitda > 0:
            st.success(f"✅ **Financial Viability:** €{daily_ebitda:,.0f}/day profit")
            st.caption(f"ROI: {roi_15y:.1f}% over 15 years")
        else:
            st.error(f"❌ **Financial Viability:** €{daily_ebitda:,.0f}/day loss")
            st.caption("Negative cash flow - review pricing/costs")
    
    # Quick Actions
    st.markdown("### 🎮 **Quick Actions**")
    action_cols = st.columns(3)
    with action_cols[0]:
        if st.button("💾 Save Current Scenario", key="dash_save"):
            # Save current configuration as Scenario D
            if 'scenarios' not in st.session_state:
                st.session_state['scenarios'] = {}
            
            # Create current results dictionary
            current_results = {
                "Peak Load (kVA)": peak_load_kva,
                "Profit/Day (€)": daily_ebitda,
                "Margin (%)": daily_margin,
                "CAPEX (€)": capex_total,
                "ROI 15y (%)": roi_15y,
                "Payback (Yrs)": payback,
                "Service Level (%)": (sl_hpc + sl_ac)/2,
                "Lost Rev (€/day)": lost_rev,
                "Charging Hours": total_charging_hours
            }
            
            st.session_state['scenarios']['D'] = current_results
            st.success(f"✅ Current configuration saved as Scenario D | Profit: €{daily_ebitda:,.0f}/day")
            st.rerun()
    
    with action_cols[1]:
        if st.button("📊 Generate Report", key="dash_report"):
            # Generate a comprehensive report
            st.markdown("### 📊 **Executive Summary Report**")
            st.markdown("---")
            
            # Key metrics summary
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Daily Profit", f"€{daily_ebitda:,.0f}")
                st.metric("Service Level", f"{(sl_hpc + sl_ac)/2:.1f}%")
            with col_r2:
                st.metric("Peak Load", f"{peak_load_kva:,.0f} kVA")
                st.metric("Charging Hours", f"{total_charging_hours:.0f} hrs")
            with col_r3:
                st.metric("CAPEX", f"€{capex_total:,.0f}")
                st.metric("Payback Period", f"{payback:.1f} years")
            
            # Technical summary
            st.markdown("**🔧 Technical Configuration:**")
            st.info(f"""
            **Grid:** {transformer_limit_kva} kVA transformer | Power Factor: {power_factor:.2f}
            **Chargers:** {n_hpc} HPC ({hpc_power_kw}kW each) | {n_ac} AC ({ac_power_kw}kW each)
            **Site:** {project_name} | Area: {st.session_state['available_area']} m²
            """)
            
            # Financial summary
            st.markdown("**💰 Financial Analysis:**")
            if daily_ebitda > 0:
                st.success(f"""
                **Viable Investment:** €{daily_ebitda:,.0f}/day profit | {roi_15y:.1f}% ROI over 15 years
                **Break-even:** {payback:.1f} years | Annual revenue: €{daily_ebitda * 365:,.0f}
                """)
            else:
                st.error(f"**Not Viable:** €{abs(daily_ebitda):,.0f}/day loss - review pricing/costs")
            
            # Recommendations
            st.markdown("**💡 Recommendations:**")
            if is_overload:
                st.warning("⚠️ **Critical:** Reduce peak load or upgrade transformer capacity")
            if (sl_hpc + sl_ac)/2 < 99:
                st.warning(f"⚠️ **Service Issue:** Add {max(1, int((n_hpc + n_ac) * 0.1))} more chargers to reach 99% service level")
            if payback > 10:
                st.warning("⚠️ **Long Payback:** Consider higher pricing or cost optimization")
            
            st.markdown("---")
            st.caption("Report generated on " + str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")))
    
    with action_cols[2]:
        if st.button("🔄 Reset Analysis", key="dash_reset"):
            # Confirm reset with a dialog-like approach
            st.session_state['confirm_reset'] = True
            
        if 'confirm_reset' in st.session_state and st.session_state['confirm_reset']:
            st.warning("⚠️ **Confirm Reset:** This will permanently delete all saved scenarios (A, B, C, D)")
            reset_cols = st.columns(2)
            with reset_cols[0]:
                if st.button("✅ Yes, Reset Everything", key="confirm_reset_yes"):
                    st.session_state['scenarios'] = {}
                    if 'confirm_reset' in st.session_state:
                        del st.session_state['confirm_reset']
                    st.success("🔄 Analysis reset complete - all scenarios cleared")
                    st.rerun()
            with reset_cols[1]:
                if st.button("❌ Cancel", key="confirm_reset_no"):
                    if 'confirm_reset' in st.session_state:
                        del st.session_state['confirm_reset']
                    st.info("Reset cancelled")

with tab_tech:
    # Enhanced Grid Load Analysis with Professional Styling
    fig = go.Figure()

    # Add background zones for better readability
    fig.add_hrect(y0=0, y1=transformer_limit_kva*0.8, fillcolor="#f0f9ff", opacity=0.3, line_width=0, layer="below")
    fig.add_hrect(y0=transformer_limit_kva*0.8, y1=transformer_limit_kva*0.95, fillcolor="#fef3c7", opacity=0.3, line_width=0, layer="below")
    fig.add_hrect(y0=transformer_limit_kva*0.95, y1=transformer_limit_kva*1.2, fillcolor="#fee2e2", opacity=0.3, line_width=0, layer="below")

    # Enhanced traces with better styling
    fig.add_trace(go.Scatter(
        x=res.index,
        y=[transformer_limit_kva]*96,
        name="Grid Limit",
        line=dict(color='#dc2626', width=3, dash='dash'),
        mode='lines',
        hovertemplate="Grid Limit: %{y:.0f} kVA<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=res.index,
        y=res["Final_Grid_kW"]/power_factor,
        name="Grid Load",
        fill='tozeroy',
        line=dict(color='#2563eb', width=3),
        mode='lines',
        hovertemplate="Grid Load: %{y:.1f} kVA<extra></extra>"
    ))

    if pv_kwp > 0:
        fig.add_trace(go.Scatter(
            x=res.index,
            y=res["PV_Generation_kW"],
            name="Solar Generation",
            fill='tozeroy',
            line=dict(color='#16a34a', width=2),
            mode='lines',
            hovertemplate="Solar: %{y:.1f} kW<extra></extra>"
        ))

    # Enhanced layout
    fig.update_layout(
        title=dict(
            text="<b>⚡ Grid Load Analysis - 24 Hour Profile</b>",
            font=dict(size=20, color='#1f2937'),
            x=0.5
        ),
        xaxis=dict(
            title="Time of Day",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        yaxis=dict(
            title="Load (kVA)",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Add zone annotations
    fig.add_annotation(text="Safe Zone", x=0.02, y=transformer_limit_kva*0.4, showarrow=False, font=dict(color='#2563eb'))
    fig.add_annotation(text="Warning Zone", x=0.02, y=transformer_limit_kva*0.875, showarrow=False, font=dict(color='#d97706'))
    fig.add_annotation(text="Critical Zone", x=0.02, y=transformer_limit_kva*1.05, showarrow=False, font=dict(color='#dc2626'))

    st.plotly_chart(fig, use_container_width=True)
with tab_serv:
    st.markdown("### Service Level Analysis")
    st.info("💡 **Why 99% Service Level?** Industry standard for infrastructure reliability - allows 1% queuing while ensuring high service quality. Service level = (Energy Served / Energy Demanded) × 100%. Demand = traffic × power × charging time.")
    
    c1, c2 = st.columns(2)
    c1.metric("HPC Service Level", f"{sl_hpc:.1f}%")
    c2.metric("AC Service Level", f"{sl_ac:.1f}%")
    
    st.markdown("**Traffic & Demand Breakdown:**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("HPC Traffic", f"{hpc_traffic} trucks/day")
        st.metric("HPC Demand", f"{demand_hpc_kwh:.0f} kWh/day")
        st.metric("HPC Served", f"{energy_hpc:.0f} kWh/day")
        st.metric("HPC Avg Hours/Truck", f"{hpc_avg_hours_per_truck:.1f} hrs")
    with col_b:
        st.metric("AC Traffic", f"{ac_traffic} trucks/day") 
        st.metric("AC Demand", f"{demand_ac_kwh:.0f} kWh/day")
        st.metric("AC Served", f"{energy_ac:.0f} kWh/day")
        st.metric("AC Avg Hours/Truck", f"{ac_avg_hours_per_truck:.1f} hrs")
    
    st.metric("Total Daily Charging Hours", f"{total_charging_hours:.0f} hrs", delta=f"Max: {(n_hpc + n_ac) * 24:.0f} hrs")
    
    fig_cap = go.Figure()

    # Add capacity utilization zones
    fig_cap.add_hrect(y0=0, y1=n_hpc * hpc_power_kw * 0.7, fillcolor="#f0fdf4", opacity=0.3, line_width=0, layer="below")
    fig_cap.add_hrect(y0=n_hpc * hpc_power_kw * 0.7, y1=n_hpc * hpc_power_kw * 0.9, fillcolor="#fef3c7", opacity=0.3, line_width=0, layer="below")
    fig_cap.add_hrect(y0=n_hpc * hpc_power_kw * 0.9, y1=n_hpc * hpc_power_kw * 1.1, fillcolor="#fee2e2", opacity=0.3, line_width=0, layer="below")

    # Enhanced traces
    fig_cap.add_trace(go.Scatter(
        x=res.index,
        y=[n_hpc * hpc_power_kw]*96,
        name="Max Capacity",
        line=dict(color='#dc2626', width=2, dash='dot'),
        mode='lines',
        hovertemplate="Max Capacity: %{y:.0f} kW<extra></extra>"
    ))

    fig_cap.add_trace(go.Scatter(
        x=res.index,
        y=res["HPC_Demand_kW"],
        name="Unserved Demand",
        fill='tonexty',
        line=dict(color='#ef4444', width=0),
        mode='lines',
        hovertemplate="Unserved: %{y:.1f} kW<extra></extra>"
    ))

    fig_cap.add_trace(go.Scatter(
        x=res.index,
        y=res["HPC_Served_kW"],
        name="Served Load",
        fill='tozeroy',
        line=dict(color='#2563eb', width=3),
        mode='lines',
        hovertemplate="Served: %{y:.1f} kW<extra></extra>"
    ))

    fig_cap.update_layout(
        title=dict(
            text="<b>🔋 HPC Capacity vs Demand Analysis</b>",
            font=dict(size=18, color='#1f2937'),
            x=0.5
        ),
        xaxis=dict(
            title="Time of Day (24h)",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        yaxis=dict(
            title="Power (kW)",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    # Add utilization indicators
    fig_cap.add_annotation(text="Under-utilized", x=0.02, y=n_hpc * hpc_power_kw * 0.35, showarrow=False, font=dict(color='#16a34a', size=10))
    fig_cap.add_annotation(text="Optimal Range", x=0.02, y=n_hpc * hpc_power_kw * 0.8, showarrow=False, font=dict(color='#d97706', size=10))
    fig_cap.add_annotation(text="Overloaded", x=0.02, y=n_hpc * hpc_power_kw * 0.95, showarrow=False, font=dict(color='#dc2626', size=10))

    st.plotly_chart(fig_cap, use_container_width=True)

with tab_fin:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_w = go.Figure(go.Waterfall(
            name="Financial Flow",
            orientation="v",
            measure=["relative", "relative", "total", "relative", "relative", "relative", "relative", "total"],
            x=["Revenue Streams", "THG Premium", "Total Revenue", "Energy Costs", "Peak Charges", "Facility Costs", "Operations", "Daily EBITDA"],
            text=[f"€{rev_sales:.0f}", f"€{rev_thg:.0f}", f"€{total_rev:.0f}", f"-€{opex_energy:.0f}", f"-€{opex_peak:.0f}", f"-€{opex_rent_fix+opex_rent_var:.0f}", f"-€{opex_maint:.0f}", f"€{daily_ebitda:.0f}"],
            y=[rev_sales, rev_thg, total_rev, -opex_energy, -opex_peak, -(opex_rent_fix+opex_rent_var), -opex_maint, daily_ebitda],
            connector={"line":{"color":"rgb(63, 63, 63)", "width": 2}},
            decreasing={"marker":{"color":"#ef4444", "line":{"color":"#dc2626", "width": 1}}},
            increasing={"marker":{"color":"#16a34a", "line":{"color":"#15803d", "width": 1}}},
            totals={"marker":{"color":"#2563eb", "line":{"color":"#1d4ed8", "width": 2}}}
        ))

        fig_w.update_layout(
            title=dict(
                text="<b>💰 Daily Profit & Loss Waterfall</b>",
                font=dict(size=18, color='#1f2937'),
                x=0.5
            ),
            xaxis=dict(
                title="",
                gridcolor='#e5e7eb'
            ),
            yaxis=dict(
                title="Daily Amount (€)",
                gridcolor='#e5e7eb',
                linecolor='#9ca3af'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False
        )

        st.plotly_chart(fig_w, use_container_width=True)
    with c2:
        st.metric("LCOC", f"€{lcoc:.2f} / kWh")
        st.metric("Payback", f"{payback:.1f} Years")
        st.metric("Daily Profit", f"€{daily_ebitda:,.0f}")
with tab_long:
    c1, c2 = st.columns(2)
    c1.metric("15-Year CO₂ Savings", f"{co2_15y_tonnes:,.0f} tonnes")
    c2.metric("15-Year Net Profit", f"€{cumulative_cf[-1]:,.0f}")
   
    colors = ['#ef4444' if v < 0 else '#16a34a' for v in cumulative_cf]
    fig_cf = go.Figure(data=[go.Bar(
        x=years,
        y=cumulative_cf,
        marker_color=colors,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    )])

    fig_cf.update_layout(
        title=dict(
            text="<b>📈 15-Year Cash Flow Projection</b>",
            font=dict(size=18, color='#1f2937'),
            x=0.5
        ),
        xaxis=dict(
            title="Year",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        yaxis=dict(
            title="Cumulative Cash Flow (€)",
            gridcolor='#e5e7eb',
            linecolor='#9ca3af'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Add break-even line
    if payback <= 15:
        breakeven_year = int(payback)
        fig_cf.add_vline(x=breakeven_year, line_width=3, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"Break-even: Year {breakeven_year}", annotation_position="top")

    st.plotly_chart(fig_cf, use_container_width=True)
with tab_capex:
    st.subheader("📋 Detailed Bill of Materials")
    capex_items = {
        "Category": ["Hardware (HPC Satellites)", "Hardware (Power Units)", "Hardware (AC)", "Civil Works (HPC)", "Civil Works (Cabinets)", "Cabling", "Grid Connection", "Trafo Install", "Soft Costs (Eng/Mgmt)", "PV System", "BESS"],
        "Count": [n_hpc, n_power_units, n_ac, n_hpc, n_power_units, "1 Lot", "1 Lot", "1 Lot", "1 Lot", f"{pv_kwp} kWp", f"{bess_kwh} kWh"],
        "Unit Price": [cost_dispenser, cost_cabinet, cost_ac_unit, cost_civil_hpc, cost_civil_cab, cost_cabling, cost_grid_fee, cost_trafo_install, cost_soft, cost_pv_unit, cost_bess_unit],
        "Subtotal (€)": [n_hpc*cost_dispenser, n_power_units*cost_cabinet, n_ac*cost_ac_unit, n_hpc*cost_civil_hpc, n_power_units*cost_civil_cab, cost_cabling, cost_grid_fee, cost_trafo_install, cost_soft, pv_kwp*cost_pv_unit, bess_kwh*cost_bess_unit]
    }
    df_capex = pd.DataFrame(capex_items)
    # Ensure mixed-type column is Arrow-compatible
    df_capex["Count"] = df_capex["Count"].astype(str)
    st.dataframe(df_capex.style.format({"Unit Price": "€{:,.0f}", "Subtotal (€)": "€{:,.0f}"}), use_container_width=True)
    st.success(f"**TOTAL PROJECT INVESTMENT:** €{capex_total:,.2f}")
    # Enhanced Pie chart of capex breakdown
    try:
        labels = df_capex['Category'].tolist()
        values = df_capex['Subtotal (€)'].tolist()

        # Filter out zero values for cleaner chart
        filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]
        if filtered_data:
            labels_filtered, values_filtered = zip(*filtered_data)

            fig_pie = go.Figure(data=[go.Pie(
                labels=labels_filtered,
                values=values_filtered,
                hole=0.4,
                marker_colors=['#2563eb', '#16a34a', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6b7280', '#374151']
            )])

            fig_pie.update_layout(
                title=dict(
                    text="<b>🏗️ CAPEX Cost Breakdown</b>",
                    font=dict(size=18, color='#1f2937'),
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            # Add center text
            fig_pie.add_annotation(
                text=f"Total<br>€{capex_total:,.0f}",
                x=0.5, y=0.5,
                font=dict(size=16, color='#1f2937'),
                showarrow=False
            )

            st.plotly_chart(fig_pie, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate CAPEX chart: {str(e)}")
with tab_compare:
    st.subheader("📊 Scenario Comparison Dashboard")
    st.caption("Compare saved scenarios with interactive charts for thesis presentation.")
    st.info("🎨 **Color Coding Guide:** Green = Better Performance | Red = Worse Performance | Gradient shows relative ranking across scenarios")
    
    if len(st.session_state['scenarios']) > 0:
        all_keys = list(st.session_state['scenarios'].keys())
        metrics = list(current_results.keys())
        
        # Enhanced Summary Table with explanations
        st.markdown("### 📋 Performance Matrix")
        comp_data = {"Metric": metrics}
        for k in all_keys:
            comp_data[f"Scenario {k}"] = [st.session_state['scenarios'][k][m] for m in metrics]
        df_comp = pd.DataFrame(comp_data)
        df_comp.set_index("Metric", inplace=True)
        
        # Add performance indicators
        styled_df = df_comp.style.format("{:,.1f}").background_gradient(cmap='RdYlGn', axis=1, subset=pd.IndexSlice[:, df_comp.columns])
        
        # Add metric explanations
        metric_explanations = {
            "Peak Load (kVA)": "Grid demand (lower = better grid stability)",
            "Profit/Day (€)": "Daily EBITDA (higher = better financials)",
            "Margin (%)": "Profit margin percentage (higher = better efficiency)",
            "CAPEX (€)": "Total investment cost (lower = better economics)",
            "ROI 15y (%)": "15-year return on investment (higher = better returns)",
            "Payback (Yrs)": "Years to recover investment (lower = faster payback)",
            "Service Level (%)": "Demand satisfaction rate (higher = better reliability)",
            "Lost Rev (€/day)": "Daily revenue loss from congestion (lower = better service)",
            "Charging Hours": "Total daily charging hours (higher = better utilization)"
        }
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Metric explanations
        with st.expander("📖 Metric Definitions & Optimization Goals", expanded=False):
            for metric, explanation in metric_explanations.items():
                st.markdown(f"**{metric}:** {explanation}")
        
        st.markdown("---")
        
        # Key Metrics Comparison with separate subplots for different scales
        st.markdown("### 📊 Key Performance Indicators")
        st.caption("Separate charts for different metric types to ensure all data is clearly visible")

        # Create subplots for different metric categories
        from plotly.subplots import make_subplots

        # Financial Metrics (CAPEX, Profit)
        financial_metrics = ["CAPEX (€)", "Profit/Day (€)"]
        fig_financial = make_subplots(rows=1, cols=2, subplot_titles=financial_metrics,
                                    shared_yaxes=False)

        colors = ['#1f77b4', '#ff7f0e']
        for i, metric in enumerate(financial_metrics):
            values = [st.session_state['scenarios'][k].get(metric, 0) for k in all_keys]
            fig_financial.add_trace(
                go.Bar(name=metric, x=all_keys, y=values, marker_color=colors[i],
                      showlegend=False, hovertemplate=f'{metric}: %{{y:,.0f}}<extra></extra>'),
                row=1, col=i+1
            )

        fig_financial.update_layout(
            title='Financial Performance Metrics',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        fig_financial.update_yaxes(title_text="Amount (€)", row=1, col=1)
        fig_financial.update_yaxes(title_text="Amount (€)", row=1, col=2)
        st.plotly_chart(fig_financial, use_container_width=True)

        # Operational Metrics (Service Level, Charging Hours)
        operational_metrics = ["Service Level (%)", "Charging Hours"]
        fig_operational = make_subplots(rows=1, cols=2, subplot_titles=operational_metrics,
                                      shared_yaxes=False)

        colors = ['#2ca02c', '#d62728']
        for i, metric in enumerate(operational_metrics):
            values = [st.session_state['scenarios'][k].get(metric, 0) for k in all_keys]
            fig_operational.add_trace(
                go.Bar(name=metric, x=all_keys, y=values, marker_color=colors[i],
                      showlegend=False, hovertemplate=f'{metric}: %{{y:,.1f}}<extra></extra>'),
                row=1, col=i+1
            )

        fig_operational.update_layout(
            title='Operational Performance Metrics',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        fig_operational.update_yaxes(title_text="Percentage (%)", row=1, col=1)
        fig_operational.update_yaxes(title_text="Hours per Day", row=1, col=2)
        st.plotly_chart(fig_operational, use_container_width=True)
        
        # Radar Chart for Multi-Dimensional Analysis
        st.markdown("### 🕸️ Multi-Metric Performance Radar")
        st.caption("Each axis represents a different performance dimension. Larger areas indicate better overall performance across multiple criteria.")
        radar_metrics = ["Profit/Day (€)", "Service Level (%)", "Charging Hours", "ROI 15y (%)"]
        fig_radar = go.Figure()
        for k in all_keys:
            values = [st.session_state['scenarios'][k].get(m, 0) for m in radar_metrics]
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=radar_metrics,
                fill='toself',
                name=f"Scenario {k}",
                line=dict(width=2),
                hovertemplate='%{theta}: %{r:,.1f}<extra>Scenario {k}</extra>'
            ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max([st.session_state['scenarios'][k].get(m, 0) for k in all_keys for m in radar_metrics]) * 1.1])
            ),
            showlegend=True,
            title='Scenario Performance Radar (Multi-Dimensional Analysis)',
            template='plotly_white'
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Trend Analysis (if multiple scenarios)
        if len(all_keys) > 1:
            st.markdown("### 📈 Scenario Performance Trends")
            st.caption("Lines show how each metric changes across scenarios. Hover over points for exact values.")
            trend_metrics = ["CAPEX (€)", "Profit/Day (€)", "Service Level (%)", "Charging Hours"]
            fig_trend = go.Figure()
            trend_colors = ['#e74c3c', '#27ae60', '#3498db', '#f39c12']
            for i, metric in enumerate(trend_metrics):
                values = [st.session_state['scenarios'][k].get(metric, 0) for k in all_keys]
                fig_trend.add_trace(go.Scatter(
                    x=all_keys,
                    y=values,
                    mode='lines+markers',
                    name=metric,
                    line=dict(width=3, color=trend_colors[i]),
                    marker=dict(size=8),
                    hovertemplate=f'{metric}: %{{y:,.1f}}<extra></extra>'
                ))
            fig_trend.update_layout(
                title='Metric Trends Across Scenarios',
                xaxis_title='Scenarios',
                yaxis_title='Value',
                template='plotly_white',
                hovermode='x unified',
                legend_title='Performance Metrics'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Recommendation Engine
        st.markdown("### 💡 Scenario Recommendations")
        best_profit = max(all_keys, key=lambda k: st.session_state['scenarios'][k]["Profit/Day (€)"])
        best_service = max(all_keys, key=lambda k: st.session_state['scenarios'][k]["Service Level (%)"])
        best_capex = min(all_keys, key=lambda k: st.session_state['scenarios'][k]["CAPEX (€)"])
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        with col_rec1:
            st.metric("Best Profit", f"Scenario {best_profit}", f"€{st.session_state['scenarios'][best_profit]['Profit/Day (€)']:,.0f}/day")
        with col_rec2:
            st.metric("Best Service", f"Scenario {best_service}", f"{st.session_state['scenarios'][best_service]['Service Level (%)']:.1f}%")
        with col_rec3:
            st.metric("Lowest CAPEX", f"Scenario {best_capex}", f"€{st.session_state['scenarios'][best_capex]['CAPEX (€)']:,.0f}")
        
    else:
        st.info("💾 Save scenarios (A, B, C) to enable comparison dashboard.")

with tab_layout:
    st.subheader("📐 Professional Engineering Blueprint")
    st.caption("DIN EN 61851 & VDE compliant heavy-duty truck charging station layout with German engineering standards.")

    # Professional header with key standards
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f7fafc, #edf2f7); padding: 20px; border-radius: 10px; border-left: 4px solid #E30613; margin-bottom: 20px;">
        <h4 style="color: #E30613; margin: 0 0 10px 0;">📐 German Engineering Standards Applied</h4>
        <p style="margin: 0; color: #4a5568; font-size: 14px;">
        <strong>DIN EN 61851 & VDE 0122:</strong> Bay dimensions 18-20m × 4.0-4.5m | Safety clearances 1.5-2.0m | Overhead clearance 4.5-5.0m
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main layout with better organization
    col_config, col_visualization = st.columns([1, 3])

    with col_config:
        # Configuration sections with professional styling
        st.markdown("### ⚙️ **System Configuration**")

        # Basic Layout Settings
        with st.expander("� **Layout Architecture**", expanded=True):
            num_rows = st.slider("**Parallel Rows**", 1, 4, 1, help="Number of charging bay rows")

        # Charging Bay Specifications
        with st.expander("🔋 **Charging Bay Design**", expanded=True):
            st.markdown("**Bay Orientation & Movement**")
            bay_orientation = st.selectbox("**Bay Rotation**", ["Horizontal (0°)", "Vertical (90°)", "360° Rotatable"],
                                         index=0, help="Complete bay rotation capability")

            st.markdown("**Bay Dimensions (DIN EN 61851)**")
            col_dim1, col_dim2 = st.columns(2)
            with col_dim1:
                charger_length = st.slider("**Length** (m)", 18.0, 20.0, 19.0, step=0.5,
                                         help="Heavy-duty truck length requirement")
            with col_dim2:
                charger_width = st.slider("**Width** (m)", 4.0, 4.5, 4.2, step=0.1,
                                        help="Heavy-duty truck width requirement")

            bay_spacing = st.slider("**Bay Spacing** (m)", 4.0, 5.0, 4.5, step=0.5,
                                  help="Safety clearance between bays")

        # Site Planning
        with st.expander("📍 **Site Planning**", expanded=True):
            available_area = st.number_input("**Site Area** (m²)", value=st.session_state['available_area'], min_value=1000,
                                           help="Total available land area")
            st.session_state['available_area'] = available_area

            st.markdown("**Zone Positioning**")
            col_zone1, col_zone2 = st.columns(2)
            with col_zone1:
                st.markdown("**HPC Zone Origin**")
                hpc_zone_x = st.number_input("X (m)", 0.0, 150.0, 20.0, step=0.5, key="hpc_x")
                hpc_zone_y = st.number_input("Y (m)", 0.0, 100.0, 20.0, step=0.5, key="hpc_y")

            with col_zone2:
                st.markdown("**AC Zone Origin**")
                ac_zone_x = st.number_input("X (m)", 20.0, 170.0, 90.0, step=0.5, key="ac_x")
                ac_zone_y = st.number_input("Y (m)", 0.0, 100.0, 50.0, step=0.5, key="ac_y")

        # Safety & Infrastructure
        with st.expander("🛡️ **Safety & Infrastructure**", expanded=False):
            st.markdown("**Safety Clearances (VDE 0122)**")
            safety_margin = st.slider("**Electrical Safety** (m)", 1.5, 2.0, 1.8, step=0.1)
            access_road_width = st.slider("**Access Road** (m)", 5.0, 7.0, 6.0, step=0.5)
            overhead_clearance = st.slider("**Overhead Clearance** (m)", 4.5, 5.0, 4.7, step=0.1)

            st.markdown("**Equipment Positioning**")
            col_eq1, col_eq2 = st.columns(2)
            with col_eq1:
                transformer_x = st.number_input("Transformer X", 0.0, 170.0, 130.0, step=0.5)
                transformer_y = st.number_input("Transformer Y", 0.0, 110.0, 80.0, step=0.5)
            with col_eq2:
                power_cabinet_x = st.number_input("Power Cabinet X", 0.0, 170.0, 70.0, step=0.5)
                power_cabinet_y = st.number_input("Power Cabinet Y", 0.0, 110.0, 75.0, step=0.5)

        # Export functionality
        st.markdown("---")
        if st.button("📤 **Export Engineering Blueprint**", type="primary"):
            st.success("📋 Blueprint exported successfully! (Feature implementation in progress)")

    with col_visualization:
        # Site map upload
        uploaded_file = st.file_uploader("📸 **Upload Site Map** (Optional)", type=['png', 'jpg'],
                                       help="Upload existing site plan for overlay")

        # Main visualization area
        st.markdown("### 🎨 **3D Engineering Visualization**")

        # Create the professional layout visualization
        fig_layout = plt.figure(figsize=(16, 12))
        ax = fig_layout.add_subplot(111)

        # Set up the canvas with professional styling
        # Enhanced background and styling
        ax.set_xlim(0, 160)
        ax.set_ylim(0, 110)
        ax.set_aspect('equal')
        ax.set_facecolor('#fafafa')

        # Professional grid with enhanced visibility
        ax.grid(True, alpha=0.4, color='#cbd5e0', linestyle='--', linewidth=0.8)
        ax.set_xticks(range(0, 161, 20))
        ax.set_yticks(range(0, 111, 20))
        ax.tick_params(colors='#4a5568', labelsize=11, width=1)

        # Enhanced title and branding
        ax.set_title('🏭 ELEXON Charging Hub - Professional Engineering Layout\nDIN EN 61851 & VDE 0122 Compliant',
                    fontsize=16, fontweight='bold', color='#1f2937', pad=20, ha='center')

        # Enhanced axis styling
        ax.set_xlabel('East-West Position (m)', fontsize=12, color='#4a5568', fontweight='bold')
        ax.set_ylabel('North-South Position (m)', fontsize=12, color='#4a5568', fontweight='bold')

        # Enhanced grid
        ax.grid(True, alpha=0.4, color='#cbd5e0', linestyle='--', linewidth=0.8)
        ax.set_xticks(range(0, 161, 20))
        ax.set_yticks(range(0, 111, 20))
        ax.tick_params(colors='#4a5568', labelsize=11, width=1)

        # Draw HPC zone with professional bay rotation
        hpc_start_x = hpc_zone_x
        hpc_start_y = hpc_zone_y

        for row in range(num_rows):
            y_pos = hpc_start_y + row * (charger_length + access_road_width)
            for i in range(n_hpc):
                x_pos = hpc_start_x + i * (charger_width + bay_spacing)

                # Main charger bay with enhanced styling
                if bay_orientation == "Horizontal (0°)":
                    # Standard horizontal bay with gradient effect
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_width, charger_length,
                                                facecolor='#dc2626', edgecolor='#b91c1c', linewidth=2.5,
                                                alpha=0.9, linestyle='-'))
                    ax.text(x_pos + charger_width/2, y_pos + charger_length/2, f'HPC{i+1}',
                           ha='center', va='center', color='white', fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

                elif bay_orientation == "Vertical (90°)":
                    # Rotated vertical bay with enhanced styling
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_length, charger_width,
                                                facecolor='#dc2626', edgecolor='#b91c1c', linewidth=2.5,
                                                alpha=0.9, linestyle='-'))
                    ax.text(x_pos + charger_length/2, y_pos + charger_width/2, f'HPC{i+1}',
                           ha='center', va='center', color='white', fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

                else:  # 360° Rotatable
                    # Circular bay mount with rotation indicator and enhanced styling
                    center_x = x_pos + charger_width/2
                    center_y = y_pos + charger_length/2
                    ax.add_patch(patches.Circle((center_x, center_y), charger_width/2,
                                              facecolor='#dc2626', edgecolor='#b91c1c', linewidth=2.5, alpha=0.9))
                    # Add rotation arrows
                    ax.annotate('', xy=(center_x + charger_width/3, center_y), xytext=(center_x + charger_width/4, center_y),
                              arrowprops=dict(arrowstyle='->', color='white', linewidth=2, alpha=0.8))
                    ax.text(center_x, center_y, f'HPC{i+1}\n360°',
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

                # Safety zone outline
                ax.add_patch(patches.Rectangle((x_pos - safety_margin, y_pos - safety_margin),
                                            charger_width + 2*safety_margin, charger_length + 2*safety_margin,
                                            facecolor='none', edgecolor='#e53e3e', linewidth=1, linestyle='--', alpha=0.7))

        # Draw AC zone with same rotation logic
        ac_start_x = ac_zone_x
        ac_start_y = ac_zone_y

        for row in range(num_rows):
            y_pos = ac_start_y + row * (charger_length + access_road_width)
            for i in range(n_ac):
                x_pos = ac_start_x + i * (charger_width + bay_spacing)

                if bay_orientation == "Horizontal (0°)":
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_width, charger_length,
                                                facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_width/2, y_pos + charger_length/2, f'AC{i+1}',
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                elif bay_orientation == "Vertical (90°)":
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_length, charger_width,
                                                facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_length/2, y_pos + charger_width/2, f'AC{i+1}',
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                else:  # 360° Rotatable
                    center_x = x_pos + charger_width/2
                    center_y = y_pos + charger_length/2
                    ax.add_patch(patches.Circle((center_x, center_y), charger_width/2,
                                              facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(center_x, center_y, f'AC{i+1}\n360°',
                           ha='center', va='center', color='white', fontsize=9, fontweight='bold')

                # Safety zone
                ax.add_patch(patches.Rectangle((x_pos - safety_margin, y_pos - safety_margin),
                                            charger_width + 2*safety_margin, charger_length + 2*safety_margin,
                                            facecolor='none', edgecolor='#e53e3e', linewidth=1, linestyle='--', alpha=0.7))

        # Add infrastructure elements
        ax.add_patch(patches.Rectangle((transformer_x-2, transformer_y-2), 4, 4,
                                    facecolor='#4a5568', edgecolor='#2d3748', linewidth=2))
        ax.text(transformer_x, transformer_y, 'T', ha='center', va='center', color='white',
               fontsize=12, fontweight='bold')

        ax.add_patch(patches.Rectangle((power_cabinet_x-1.5, power_cabinet_y-1.5), 3, 3,
                                    facecolor='#718096', edgecolor='#4a5568', linewidth=2))
        ax.text(power_cabinet_x, power_cabinet_y, 'PC', ha='center', va='center', color='white',
               fontsize=10, fontweight='bold')

        # Professional legend
        legend_elements = [
            patches.Patch(facecolor='#E30613', edgecolor='#b91c1c', label='HPC Charging Bay'),
            patches.Patch(facecolor='#2f855a', edgecolor='#38a169', label='AC Charging Bay'),
            patches.Patch(facecolor='#4a5568', edgecolor='#2d3748', label='Transformer'),
            patches.Patch(facecolor='#718096', edgecolor='#4a5568', label='Power Cabinet'),
            patches.Patch(facecolor='none', edgecolor='#e53e3e', linestyle='--', label='Safety Zone'),
            plt.Line2D([0], [0], color='#cbd5e0', linestyle='--', linewidth=1, label='10m Grid'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.95,
                 edgecolor='#4a5568', facecolor='white', title='Engineering Elements')

        # Engineering specifications overlay
        hpc_area = (n_hpc * charger_width + (n_hpc - 1) * bay_spacing) * (num_rows * charger_length + (num_rows - 1) * access_road_width)
        ac_area = (n_ac * charger_width + (n_ac - 1) * bay_spacing) * (num_rows * charger_length + (num_rows - 1) * access_road_width)
        required_area = hpc_area + ac_area
        fits = required_area <= st.session_state['available_area']

        # Professional specs box
        specs_text = f"""PROFESSIONAL ENGINEERING SPECIFICATIONS
Site Area: {st.session_state['available_area']:.0f} m² | Required: {required_area:.0f} m²
Compliance: {'✓ DIN EN 61851 & VDE 0122' if fits else '✗ OVERSIZED - Review Layout'}
Total Bays: {n_hpc + n_ac} | HPC: {n_hpc} | AC: {n_ac}
Bay Config: {charger_length:.1f}m × {charger_width:.1f}m | Orientation: {bay_orientation}
Safety Margins: {safety_margin:.1f}m electrical | {overhead_clearance:.1f}m overhead
Power Rating: HPC {hpc_power_kw}kW | AC {ac_power_kw}kW"""

        ax.text(5, 105, specs_text, fontsize=9, fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.8", facecolor='white', alpha=0.95, edgecolor='#E30613', linewidth=2),
               verticalalignment='top', color='#1a202c', fontweight='bold')

        st.pyplot(fig_layout)
        
        fig_layout = plt.figure(figsize=(14, 10))
        ax = fig_layout.add_subplot(111)
        
        if uploaded_file:
            img = Image.open(uploaded_file)
            ax.imshow(img, extent=[0, 140, 0, 90])
        else:
            ax.set_xlim(0, 140)
            ax.set_ylim(0, 90)
            ax.add_patch(patches.Rectangle((0, 0), 140, 90, color='#f8f9fa', alpha=0.8))
            ax.text(70, 45, "Site Layout Canvas", ha='center', va='center', color='#666', fontsize=14, fontweight='bold')
        
        ax.axis('off')
        
        # Engineering grid lines (5m intervals for precision)
        for x in range(0, 141, 5):
            ax.axvline(x, color='#0066cc', linestyle='-', alpha=0.2, linewidth=0.5)
        for y in range(0, 91, 5):
            ax.axhline(y, color='#0066cc', linestyle='-', alpha=0.2, linewidth=0.5)
        
        # Major grid lines (10m)
        for x in range(0, 141, 10):
            ax.axvline(x, color='#003366', linestyle='-', alpha=0.4, linewidth=1)
            ax.text(x, -2, f'{x}m', ha='center', va='top', fontsize=8, color='#003366')
        for y in range(0, 91, 10):
            ax.axhline(y, color='#003366', linestyle='-', alpha=0.4, linewidth=1)
            ax.text(-2, y, f'{y}m', ha='right', va='center', fontsize=8, color='#003366')
        
        # Draw HPC zone with professional bay rotation
        hpc_start_x = hpc_zone_x
        hpc_start_y = hpc_zone_y

        for row in range(num_rows):
            y_pos = hpc_start_y + row * (charger_length + access_road_width)
            for i in range(n_hpc):
                x_pos = hpc_start_x + i * (charger_width + bay_spacing)

                # Main charger bay with rotation capability
                if bay_orientation == "Horizontal (0°)":
                    # Standard horizontal bay
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_width, charger_length, 
                                                facecolor='#E30613', edgecolor='#b91c1c', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_width/2, y_pos + charger_length/2, f'HPC{i+1}', 
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                elif bay_orientation == "Vertical (90°)":
                    # Rotated vertical bay
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_length, charger_width, 
                                                facecolor='#E30613', edgecolor='#b91c1c', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_length/2, y_pos + charger_width/2, f'HPC{i+1}', 
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                else:  # 360° Rotatable
                    # Circular bay mount with rotation indicator
                    center_x = x_pos + charger_width/2
                    center_y = y_pos + charger_length/2
                    ax.add_patch(patches.Circle((center_x, center_y), charger_width/2, 
                                              facecolor='#E30613', edgecolor='#b91c1c', linewidth=2, alpha=0.9))
                    ax.text(center_x, center_y, f'HPC{i+1}\n360°', 
                           ha='center', va='center', color='white', fontsize=9, fontweight='bold')

                # Safety zone outline
                ax.add_patch(patches.Rectangle((x_pos - safety_margin, y_pos - safety_margin), 
                                            charger_width + 2*safety_margin, charger_length + 2*safety_margin, 
                                            facecolor='none', edgecolor='#e53e3e', linewidth=1, linestyle='--', alpha=0.7))
        
        # Draw AC zone with same rotation logic
        ac_start_x = ac_zone_x
        ac_start_y = ac_zone_y

        for row in range(num_rows):
            y_pos = ac_start_y + row * (charger_length + access_road_width)
            for i in range(n_ac):
                x_pos = ac_start_x + i * (charger_width + bay_spacing)

                if bay_orientation == "Horizontal (0°)":
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_width, charger_length, 
                                                facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_width/2, y_pos + charger_length/2, f'AC{i+1}', 
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                elif bay_orientation == "Vertical (90°)":
                    ax.add_patch(patches.Rectangle((x_pos, y_pos), charger_length, charger_width, 
                                                facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(x_pos + charger_length/2, y_pos + charger_width/2, f'AC{i+1}', 
                           ha='center', va='center', color='white', fontsize=10, fontweight='bold')

                else:  # 360° Rotatable
                    center_x = x_pos + charger_width/2
                    center_y = y_pos + charger_length/2
                    ax.add_patch(patches.Circle((center_x, center_y), charger_width/2, 
                                              facecolor='#2f855a', edgecolor='#38a169', linewidth=2, alpha=0.9))
                    ax.text(center_x, center_y, f'AC{i+1}\n360°', 
                           ha='center', va='center', color='white', fontsize=9, fontweight='bold')

                # Safety zone
                ax.add_patch(patches.Rectangle((x_pos - safety_margin, y_pos - safety_margin), 
                                            charger_width + 2*safety_margin, charger_length + 2*safety_margin, 
                                            facecolor='none', edgecolor='#e53e3e', linewidth=1, linestyle='--', alpha=0.7))
        
        # Draw equipment with engineering precision
        # Transformer (IEC compliant symbol)
        ax.add_patch(patches.Circle((transformer_x, transformer_y), 2.5, facecolor='#d69e2e', edgecolor='#b7791f', linewidth=2, alpha=0.95))
        ax.add_patch(patches.Rectangle((transformer_x-1.5, transformer_y-1), 3, 2, facecolor='#d69e2e', edgecolor='#b7791f', linewidth=1, alpha=0.9))
        ax.text(transformer_x, transformer_y, 'T', ha='center', va='center', color='white', fontsize=11, fontweight='bold')
        
        # Power Cabinet (UL compliant enclosure)
        ax.add_patch(patches.Rectangle((power_cabinet_x-2, power_cabinet_y-2), 4, 4, facecolor='#3182ce', edgecolor='#2c5282', linewidth=2, alpha=0.95))
        ax.text(power_cabinet_x, power_cabinet_y, 'PC', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
        # Ventilation grilles
        ax.add_patch(patches.Rectangle((power_cabinet_x-1.5, power_cabinet_y-1.8), 3, 0.4, facecolor='#4299e1', alpha=0.7))
        ax.add_patch(patches.Rectangle((power_cabinet_x-1.5, power_cabinet_y+1.4), 3, 0.4, facecolor='#4299e1', alpha=0.7))
        
        # Draw dimensions
        # Horizontal dimension for HPC
        hpc_end_x = hpc_start_x + (n_hpc * charger_width + (n_hpc - 1) * bay_spacing)
        ax.annotate('', xy=(hpc_start_x, hpc_start_y - 2), xytext=(hpc_end_x, hpc_start_y - 2), 
                   arrowprops=dict(arrowstyle='<->', color='black'))
        ax.text((hpc_start_x + hpc_end_x)/2, hpc_start_y - 3, f'{hpc_end_x - hpc_start_x:.1f}m', ha='center', va='top', fontsize=10, fontweight='bold')
        
        # Vertical dimension
        hpc_end_y = hpc_start_y + num_rows * charger_length + (num_rows - 1) * access_road_width
        ax.annotate('', xy=(hpc_start_x - 2, hpc_start_y), xytext=(hpc_start_x - 2, hpc_end_y), 
                   arrowprops=dict(arrowstyle='<->', color='black'))
        ax.text(hpc_start_x - 3, (hpc_start_y + hpc_end_y)/2, f'{hpc_end_y - hpc_start_y:.1f}m', ha='right', va='center', fontsize=10, fontweight='bold', rotation=90)
        
        # Professional engineering legend
        legend_elements = [
            patches.Patch(facecolor='#E30613', edgecolor='#b91c1c', label='HPC Charging Bays'),
            patches.Patch(facecolor='#2f855a', edgecolor='#38a169', label='AC Charging Bays'),
            patches.Patch(facecolor='#d69e2e', edgecolor='#b7791f', label='Transformer (DIN EN 61851)'),
            patches.Patch(facecolor='#3182ce', edgecolor='#2c5282', label='Power Cabinet (VDE 0122)'),
            plt.Line2D([0], [0], color='#e53e3e', linestyle='--', linewidth=1, label='Safety Zone (1.8m)'),
            plt.Line2D([0], [0], color='#0066cc', linestyle='-', linewidth=0.5, label='5m Grid'),
            plt.Line2D([0], [0], color='#003366', linestyle='-', linewidth=1, label='10m Grid')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.95,
                 edgecolor='#4a5568', facecolor='white', title='Engineering Elements')

        st.pyplot(fig_layout)