# ELEXON DIGITAL TWIN - Quick Walkthrough Guide

## 🚀 GETTING STARTED

**Access:** https://elexon-digital-twin-gis.streamlit.app

**First View:** Professional header with project configuration sidebar

---

## 📍 SIDEBAR CONTROLS (LEFT)

### Project Configuration
- **Project Name:** Set custom name (e.g., "A9 Schkeuditz Hub")
- **Site Location:** 
  - Enter address manually
  - Input GPS coordinates (latitude/longitude)
  - Links to GIS map with purple star marker

### Financial Parameters
- **Tariff Rates:** HPC €0.75/kWh, AC €0.50/kWh, Parking fees
- **Energy Costs:** Grid electricity €0.15/kWh, Solar €0.08/kWh
- **Investment:** CAPEX inputs for chargers, infrastructure, renewables

### Operational Settings
- **Charger Mix:** Number of HPC (350kW) and AC (22kW) stations
- **Battery Storage:** Capacity (kWh) and power (kW)
- **Solar PV:** Array size (kWp)
- **Queue Targets:** Service level goals (95-99%)

---

## 🎯 MAIN TABS (TOP)

### 1️⃣ DASHBOARD TAB
**Purpose:** Real-time performance overview

**Key Metrics (Top Cards):**
- **Peak Load:** Maximum grid demand in kW
- **Daily Profit:** Net EBITDA per day in €
- **Service Level:** Availability percentage (target: 99%+)
- **Energy Served:** Daily kWh delivered to trucks
- **Utilization:** Charger usage percentage

**Sidebar Monitors:**
- **Grid Status:** Green (operational) or Red (overloaded)
- **Service Quality:** Excellent/Good/Needs Improvement
- **Financial Status:** Profitable or Loss with ROI details

**Main Charts:**
- Revenue breakdown (HPC, AC, Parking, Energy)
- Cost structure (Energy, O&M, Labor, Grid)
- Hourly demand pattern (24-hour cycle)
- Monthly trends (seasonal variations)

**Scenario Comparison:**
- Save configurations as A, B, C
- Compare side-by-side metrics
- Automated best-scenario recommendations

---

### 2️⃣ FINANCIAL ANALYSIS TAB
**Purpose:** 15-year investment evaluation

**Sections:**

**A) CAPEX Breakdown**
- Hardware costs (chargers, transformers)
- Civil works (construction, site prep)
- Grid connection fees
- Renewable energy systems (solar, BESS)
- Total investment summary

**B) OPEX Modeling**
- Annual energy costs
- Maintenance and labor
- Insurance and lease
- 15-year cumulative costs

**C) Revenue Projections**
- HPC charging income
- AC charging income
- Parking and ancillary services
- Growth assumptions

**D) Profitability Metrics**
- **NPV (15-year):** Net Present Value at 8% discount
- **IRR:** Internal Rate of Return
- **Payback Period:** Years to break even
- **ROI:** Return on Investment percentage

**E) Cash Flow Analysis**
- Year-by-year profit/loss
- Cumulative cash flow chart
- Break-even visualization

**F) Sensitivity Analysis**
- Vary demand ±20%
- Vary tariffs ±€0.10/kWh
- Tornado chart showing impact

---

### 3️⃣ OPERATIONAL OPTIMIZATION TAB
**Purpose:** Queue management and service quality

**Sections:**

**A) Demand Profile**
- Hourly arrival rates (trucks/hour)
- Peak periods identification
- Seasonal patterns

**B) Queue Simulation (Erlang-C)**
- Average wait time in minutes
- Queue length analysis
- Service level achievement (target: 99%)
- Lost revenue from queuing

**C) Charger Utilization**
- HPC vs AC usage split
- Total charging hours per day
- Idle time analysis

**D) Energy Management**
- Grid import vs Solar generation
- Battery charge/discharge patterns
- Peak shaving effectiveness

**E) Optimization Recommendations**
- Suggested charger additions
- Optimal BESS sizing
- Service improvement actions

---

### 4️⃣ GIS DIGITAL TWIN TAB
**Purpose:** Site selection and geographic analysis

**Features:**

**Interactive Map:**
- 90+ pre-scored sites across German highways
- Color-coded markers:
  - Green: Excellent sites (score 90-100)
  - Yellow: Good sites (score 70-89)
  - Red: Poor sites (score <70)
  - Purple Star: Your manual location

**Site Information (Click Marker):**
- Highway corridor (e.g., A9, A3)
- Grid capacity (kVA available)
- Traffic density (trucks/day)
- Competition index
- Financial score
- Overall ranking

**Control Panel:**
- **Scoring Weights:** Adjust importance of:
  - Grid availability (0-100%)
  - Traffic density (0-100%)
  - Competition (0-100%)
- **Filter Sites:** 
  - Minimum grid capacity
  - Minimum traffic
  - Specific highway corridors
- **Export:** Download scored sites as CSV

**Site Selection:**
- Click "Set Active Site" button on any marker
- Coordinates transfer to Layout tab
- Site data populates sidebar inputs

---

### 5️⃣ SERVICE LEVEL TAB
**Purpose:** Compliance and quality monitoring

**Sections:**

**A) Compliance Dashboard**
- **DIN EN 61851:** Charging standards (PASS/WARNING/FAIL)
- **VDE 0122:** German electrical safety
- **EN 50160:** Grid quality standards
- **ISO 15118:** Communication protocols

**B) Service Quality Metrics**
- Availability percentage (uptime)
- Average charging speed (kW)
- Wait time analysis
- Customer satisfaction proxy

**C) Queue Management**
- Real-time queue length
- Historical wait times
- Service degradation alerts

**D) Performance Gauges**
- Service Level: Color-coded 0-100%
- Utilization Rate: Optimal range 60-80%
- Grid Stability: Voltage quality

**E) Incident Tracking**
- Downtime events
- Maintenance logs
- Compliance violations

---

### 6️⃣ LAYOUT TAB
**Purpose:** Engineering blueprint design

**Features:**

**Site Context Integration:**
- Mini-map showing selected GIS site
- Available area from site data
- Grid capacity constraints
- 100m reference circle

**Configuration Panel (3 Tabs):**

**Tab 1: Zone Layout**
- Interactive X/Y positioning
- Drag zones on blueprint:
  - HPC charging zone
  - AC charging zone
  - Transformer station
  - Battery storage
  - Solar PV array
  - Control building

**Tab 2: Bay Design**
- Bay dimensions (18-20m × 4-5m)
- Safety clearances (1.5-2.0m)
- Overhead clearance (4.5-5.0m)
- Number of bays per zone

**Tab 3: Safety & Equipment**
- Fire suppression zones
- Emergency exits
- Lighting layout
- Access roads
- Parking areas

**Live Blueprint:**
- Real-time 2D visualization
- Color-coded zones
- Dimension annotations
- DIN/VDE compliance markers
- Export as PNG

---

## 📄 PDF REPORT GENERATION

**Location:** Bottom of Financial Analysis tab

**Contents (6 Professional Pages):**

1. **Executive Summary**
   - Project overview
   - Key financial metrics (NPV, IRR, Payback)
   - Investment recommendation

2. **Financial Analysis**
   - CAPEX breakdown table
   - OPEX summary
   - Revenue projections
   - Profitability metrics

3. **Operational Performance**
   - Service level achievements
   - Energy metrics
   - Utilization rates
   - Solar/BESS contribution

4. **Queue & Service Metrics**
   - Wait time analysis
   - Queue length statistics
   - Lost revenue calculations
   - Optimization suggestions

5. **Compliance Status**
   - DIN EN 61851 checklist
   - VDE 0122 verification
   - Grid code compliance
   - Safety standards

6. **Risk Analysis**
   - Sensitivity to demand changes
   - Tariff impact analysis
   - Grid constraint risks
   - Mitigation strategies

**Export:** Click "Generate Professional PDF Report" button

---

## 💡 TYPICAL WORKFLOWS

### Workflow 1: New Site Evaluation
1. Go to **GIS Digital Twin** tab
2. Explore scored sites on map
3. Click marker → "Set Active Site"
4. Review site data in sidebar
5. Go to **Financial Analysis** tab
6. Adjust CAPEX/OPEX for site specifics
7. Check NPV and IRR
8. Go to **Operational** tab
9. Verify service levels achievable
10. Generate PDF report

### Workflow 2: Design Optimization
1. Start in **Dashboard** tab
2. Set baseline configuration in sidebar
3. Save as "Scenario A"
4. Go to **Operational** tab
5. Check queue performance
6. Adjust charger numbers if needed
7. Return to **Dashboard**
8. Save as "Scenario B"
9. Compare scenarios
10. Select best option

### Workflow 3: Layout Planning
1. Select site in **GIS** tab
2. Go to **Layout** tab
3. Review site context (area, grid)
4. Configure zones in control panel
5. Position equipment on blueprint
6. Verify DIN/VDE compliance
7. Export blueprint
8. Include in PDF report

---

## 🎨 VISUAL GUIDE

**Color Coding:**
- **Green:** Positive metrics, operational systems, excellent scores
- **Yellow:** Warning thresholds, good scores, optimization needed
- **Red:** Critical issues, poor performance, failures
- **Blue:** Information, neutral metrics, selected items
- **Purple:** Custom locations, special markers

**Card Styling:**
- Gradient backgrounds
- Color-coded left borders
- Shadow effects for depth
- Professional typography

---

## 📊 KEY PERFORMANCE INDICATORS

**Financial:**
- NPV > €1M = Excellent
- IRR > 15% = Good investment
- Payback < 7 years = Acceptable

**Operational:**
- Service Level > 99% = Excellent
- Utilization 60-80% = Optimal
- Wait Time < 10 min = Acceptable

**Site Scoring:**
- Score > 90 = Priority sites
- Score 70-89 = Good candidates
- Score < 70 = Avoid

---

## 🔧 TIPS FOR SUPERVISORS

1. **Start Simple:** Use default settings first, then customize
2. **Focus on NPV:** Primary financial decision metric
3. **Check Service Levels:** Must exceed 95% for viability
4. **Use GIS First:** Identify best sites before detailed analysis
5. **Compare Scenarios:** Save 2-3 options for comparison
6. **Generate PDF:** Professional output for stakeholder meetings
7. **Monitor Dashboard:** Quick health check in 30 seconds

---

## 📞 SUPPORT

For questions or detailed demonstrations, please contact the project team.

**Platform Status:** https://elexon-digital-twin-gis.streamlit.app
**Last Updated:** December 16, 2025
