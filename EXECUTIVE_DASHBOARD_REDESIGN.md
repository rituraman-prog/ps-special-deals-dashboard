# Executive Dashboard Redesign

## Overview

The Professional Services Special Terms Dashboard has been completely redesigned with a modern, executive-style layout suitable for Professional Services leadership reporting.

## Key Design Principles

### Clean & Professional
- Light gray background (#F7F9FC)
- White cards with subtle shadows
- Minimal borders and decorative elements
- Rounded corners (8px)
- Salesforce Blue (#0176D3) as primary accent

### Typography
- Font: Inter (professional, readable)
- Clear hierarchy with appropriate font sizes
- Consistent letter spacing and line heights

### Layout
- Maximum width: 1600px (optimal for leadership dashboards)
- Spacious padding (32-40px)
- Responsive grid system
- Clean white space

## Dashboard Components

### 1. Header Section
**Title**: Professional Services Special Terms Dashboard  
**Subtitle**: Overview of booked Professional Services projects and opportunities with special commercial terms.

- Clean white background
- Simple two-line layout
- No decorative elements or gradients

### 2. Navigation Bar
Simple horizontal navigation with:
- Dashboard
- Regional Analysis
- Upload Data
- All Projects
- Upload History

**Active State**: Thin Salesforce Blue (#0176D3) underline

### 3. Filters Bar
Quick filters at the top:
- Region dropdown
- Special Term dropdown
- Status dropdown
- Booking Date input

**Style**: Clean white inputs with subtle borders, focus state in Salesforce Blue

### 4. KPI Cards (4 Equal Cards)

Each card displays:
- Simple icon
- Label (uppercase, 13px)
- Large bold number (36px)
- Thin colored accent line at top (3px)

**Accent Colors**:
1. Total Special Deals - Salesforce Blue (#0176D3)
2. Framework Deals - Teal (#00A1A9)
3. Holdback Deals - Orange (#F4A261)
4. Umbrella Deals - Green (#2E844A)

**Hover Effect**: Subtle shadow elevation

### 5. Main Chart - Regional Breakdown

**Title**: Professional Services Special Terms by Region  
**Subtitle**: Distribution of booked Professional Services projects with special terms across regions.

**Chart Type**: Horizontal Stacked Bar Chart

**Features**:
- Y-axis: Regions (top 10, sorted by total deals)
- X-axis: Number of booked projects
- Stacked by special term type
- Professional muted colors for each term
- Total count displayed at end of each bar
- Interactive tooltips showing:
  - Region name
  - Special term
  - Project count
  - Percentage of total
  - Total for region

**Special Terms Included**:
- Framework (#0176D3 - Salesforce Blue)
- Holdback (#F4A261 - Orange)
- Umbrella (#2E844A - Green)
- Invoice with Subtotal(s) (#7F8FA4 - Gray)
- Separate Invoices (#00A1A9 - Teal)
- AWS SI Funding (#9D4FBB - Purple)
- PubSec OF/SOW (#E07B39 - Orange)
- Framework + Holdback (#C23934 - Red)
- Quarterly (#5C6AC4 - Blue)

**Chart Height**: 500px

### 6. Secondary Analytics (2 Cards Side-by-Side)

#### Left Card: Special Terms Distribution by Type
- **Chart Type**: Donut Chart
- **Shows**: Proportion of each special term across all deals
- **Height**: 320px
- **Legend**: Right side, compact

#### Right Card: Top 5 Regions by Total Special Deals
- **Chart Type**: Horizontal Bar Chart
- **Shows**: Top 5 regions ranked by total special deals
- **Color**: Salesforce Blue
- **Height**: 320px

### 7. Project Details Table

**Header**:
- Title: "Project Details"
- Search box on the right

**Columns**:
1. PSA Project Name
2. Opportunity Name
3. Region
4. Special Term (with badge styling)
5. Deal Status
6. Booking Date

**Features**:
- Searchable (real-time filtering)
- Filterable by region, term, status, date
- Hover effect on rows
- Clean typography
- 100 records displayed (top)

**Badge Styling**:
- Framework: Light blue background (#E8F4FD), blue text
- Holdback: Light orange background (#FFF4E8), orange text
- Umbrella: Light green background (#E8F5EC), green text

### 8. Other Tabs

#### Regional Analysis
- Comprehensive table with regional breakdowns
- Shows: Region, Total Projects, Holdback, Framework, Umbrella, Excluded, Total Amount

#### Upload Data
- Clean upload zone with dashed border
- Instructions for Salesforce export
- Drag & drop support
- Choose file button (Salesforce Blue)

#### All Projects
- Full project listing with filters
- Export CSV button
- Refresh button

#### Upload History
- List of past uploads
- File name, date, record count

## Color Palette

### Primary Colors
- **Salesforce Blue**: #0176D3 (primary accent, buttons, active states)
- **Teal**: #00A1A9 (secondary accent)
- **Orange**: #F4A261 (Holdback, warnings)
- **Green**: #2E844A (Umbrella, success)

### Neutral Colors
- **Background**: #F7F9FC (light gray)
- **Card Background**: #FFFFFF (white)
- **Text Primary**: #1A252F (dark)
- **Text Secondary**: #3E4C59 (medium)
- **Text Tertiary**: #5B6B79, #6E7985 (light)
- **Borders**: #E5E9EB, #D1D9E0 (subtle gray)

### Chart Colors (Special Terms)
Each special term has a distinct, professional color for easy identification in stacked charts.

## Responsive Design

### Desktop (> 1200px)
- 4 KPI cards in one row
- 2 secondary charts side-by-side
- Full table width

### Tablet (768px - 1200px)
- 2 KPI cards per row
- Secondary charts stack vertically

### Mobile (< 768px)
- 1 KPI card per column
- All elements stack vertically
- Reduced padding
- Smaller font sizes
- Full-width inputs

## Technical Implementation

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Flexbox and Grid layouts
- **Chart.js 4.4.0**: All visualizations
- **Vanilla JavaScript**: No dependencies beyond Chart.js

### Backend
- **Flask**: Python web framework
- **SQLite**: Database
- **REST API**: JSON endpoints

### API Endpoints
- `/api/stats`: KPI summary
- `/api/region-summary`: Regional and special terms data
- `/api/opportunities`: Full project listing
- `/api/upload`: CSV file upload

### Auto-Refresh
- Dashboard refreshes every 30 seconds
- KPIs, charts, and data automatically update

## Accessibility

- High contrast text
- Clear visual hierarchy
- Readable font sizes (minimum 11px)
- Semantic HTML elements
- Keyboard navigation support
- ARIA labels where appropriate

## Performance

- Lightweight CSS (no heavy frameworks)
- Optimized chart rendering
- Minimal JavaScript
- Fast API responses
- Efficient database queries

## Executive Features

✅ **Clean, distraction-free design**  
✅ **Data-driven insights at a glance**  
✅ **Professional color scheme**  
✅ **Easy to present in meetings**  
✅ **Responsive for all devices**  
✅ **Printable (simplified layout)**  
✅ **Auto-refreshing data**  
✅ **Searchable and filterable**

## Usage

1. **Access Dashboard**: http://localhost:5001
2. **View KPIs**: See total special deals at a glance
3. **Analyze Regions**: Review horizontal stacked bar chart
4. **Explore Details**: Use secondary charts for deeper insights
5. **Search Projects**: Filter and search in detail table
6. **Export Data**: Use export buttons in All Projects tab

## Comparison to Previous Design

### Previous Design
- Warm color palette (orange, coral)
- Decorative elements (gradients, glows, animations)
- Vertical stacked bar chart
- Floating icons and pulse animations
- Outfit + Manrope fonts

### New Executive Design
- Professional blue/neutral palette
- Minimal decorative elements
- Horizontal stacked bar chart (better for regions)
- Clean, static design
- Inter font (business standard)
- More special terms support
- Secondary analytics charts
- Better for executive presentations

## Maintenance

The dashboard is designed for:
- Easy content updates
- Simple color scheme changes
- Flexible data additions
- Minimal technical overhead

All styling is centralized in `static/style.css`.  
All chart logic is in `templates/index.html`.  
All data logic is in `app.py`.

---

**Dashboard Status**: ✅ Live at http://localhost:5001

**Last Updated**: 2026-08-20

**Design Version**: Executive v1.0
