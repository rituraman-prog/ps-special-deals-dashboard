# 📊 Combined Chart - Special Terms by Region (%)

## ✅ What Changed

I've **combined** the two separate charts into **ONE powerful visualization** that shows:

**Special Terms Breakdown by Region on a Percentage Basis**

---

## 🎯 What You'll See Now

### Single Full-Width Chart

**Title**: "🌍 Special Terms Breakdown by Region (%)"

**Type**: Stacked Percentage Bar Chart

**Shows**: 
- X-axis: Top 10 regions
- Y-axis: Percentage (0-100%)
- Bars: Stacked by special term type
- Each bar shows the proportion of deal types within that region

---

## 📊 How to Read the Chart

### Example:
If you see a region's bar:
- **Pink segment (50%)**: 50% of that region's deals are Holdback
- **Blue segment (30%)**: 30% are Framework  
- **Green segment (20%)**: 20% are Umbrella
- **Total**: Always adds up to 100%

### Colors:
- 🟣 **Pink/Purple**: Holdback deals
- 🔵 **Blue**: Framework deals
- 🟢 **Green**: Umbrella deals
- 🟠 **Orange**: Separate Invoices
- 🟣 **Purple**: Quarterly
- ⚫ **Gray**: Other types

---

## 💡 What This Tells You

### Regional Patterns:
- **Which regions have more Holdback deals?**
- **Which regions prefer Framework agreements?**
- **Are there regional differences in deal structures?**

### Quick Insights:
- Hover over any segment to see exact percentage
- Compare regions side-by-side
- Identify regional preferences instantly
- Spot outliers or unusual patterns

---

## 🎨 Chart Features

### Interactive:
- **Hover** over segments: See exact percentages
- **Hover tooltip** shows:
  - Deal type name
  - Percentage in that region
  - Total percentage shown

### Visual:
- **Smooth animations**: Bars grow from bottom
- **Color-coded legend**: At bottom of chart
- **Professional styling**: Gradient colors
- **Clear labels**: Region names on X-axis

### Technical:
- **Stacked bars**: Each region = 100%
- **Top 10 regions**: Shows highest volume regions
- **Real-time data**: Updates every 30 seconds
- **Responsive**: Resizes with window

---

## 📈 Benefits Over Two Separate Charts

### Before:
- Chart 1: Total projects by region
- Chart 2: Overall special terms distribution
- **Problem**: Can't see regional breakdown of deal types

### After:
- **One chart** shows everything
- **Percentage-based** = easy comparisons
- **Regional patterns** = immediately visible
- **Space-efficient** = more room for data

---

## 🎯 View Your New Chart

**Steps:**

1. **Open**: http://localhost:5001

2. **Hard refresh** (very important!):
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **Scroll down** to charts section

4. **Look for**: Full-width chart titled "Special Terms Breakdown by Region (%)"

5. **Hover** over bars to explore the data

---

## 🐛 If Chart Doesn't Appear

### Quick Fixes:

1. **Hard Refresh**:
   ```
   Ctrl + Shift + R (Windows)
   Cmd + Shift + R (Mac)
   ```

2. **Check Browser Console**:
   - Press F12
   - Click "Console" tab
   - Look for: "✅ Combined stacked percentage chart created!"

3. **Verify API**:
   ```
   Open: http://localhost:5001/api/region-summary
   Should show JSON data with region_term_breakdown
   ```

4. **Restart Dashboard**:
   ```bash
   cd ~/salesforce-opportunity-tool
   pkill -9 -f "python.*app.py"
   ./start_full_automation.sh
   ```

---

## 📊 Sample Data Interpretation

### Example Chart Reading:

**APAC India** (hypothetical):
- 40% Holdback (pink)
- 35% Framework (blue)
- 25% Umbrella (green)
- **Insight**: Balanced mix, slight Holdback preference

**EMEA UKI** (hypothetical):
- 60% Framework (blue)
- 30% Holdback (pink)
- 10% Other (gray)
- **Insight**: Strong Framework preference

**LATAM Brazil** (hypothetical):
- 70% Umbrella (green)
- 20% Holdback (pink)
- 10% Framework (blue)
- **Insight**: Umbrella deals dominate

---

## ✅ Success Indicators

After refreshing, you should see:

- ✅ Single full-width chart
- ✅ Colorful stacked bars
- ✅ Region names on bottom
- ✅ Percentage (0-100%) on left
- ✅ Legend at bottom showing deal types
- ✅ Smooth animation when loading
- ✅ Interactive tooltips on hover

---

## 🎉 You're Done!

Your dashboard now shows:
- **Combined visualization**
- **Percentage-based analysis**
- **Regional patterns** at a glance
- **Professional appearance**

**Refresh your browser now to see the new combined chart!** 🚀

Open: http://localhost:5001
