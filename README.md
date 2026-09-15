# Professional Services Special Deals Dashboard

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Click_Here-success?style=for-the-badge)](https://kept-themselves-sales-arrow.trycloudflare.com)
[![GitHub](https://img.shields.io/badge/GitHub-Public-blue?style=for-the-badge&logo=github)](https://github.com/rituraman-prog/ps-special-deals-dashboard)
[![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge)]()

> 🌐 **[VIEW LIVE DASHBOARD →](https://kept-themselves-sales-arrow.trycloudflare.com)**

An executive-style analytics dashboard for tracking Professional Services projects with special commercial terms. Built for Salesforce Org62 teams.

---

## 🎯 What You Can Do

- 📊 **View Real-Time KPIs**: Total deals, Framework, Holdback, Umbrella counts
- 📈 **Interactive Charts**: Regional breakdown with horizontal stacked bars  
- 🔍 **Advanced Filters**: Filter by region, special term, status, and date
- 🌐 **Access Anywhere**: Share the public URL with your team
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

---

## ✨ Features

- 📊 **Interactive Dashboard** - View statistics and recent opportunities
- 📤 **CSV Upload** - Upload Salesforce report exports with drag & drop
- 🔍 **Search & Filter** - Find opportunities quickly
- 📈 **Analytics** - Track total revenue and booking trends
- 📜 **Upload History** - Monitor data refresh activity
- 💾 **Data Storage** - Automatic storage in local SQLite database

## 🚀 Quick Start

### 1. Start the Server

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python app.py
```

### 2. Open in Browser

Go to: **http://localhost:5001**

### 3. Upload Your Data

1. Export your Salesforce report as CSV
2. Click **Upload Data** tab
3. Drag & drop or choose your CSV file
4. View your dashboard!

**See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.**

## 📋 How to Export from Salesforce

1. Log into Salesforce: https://org62.lightning.force.com
2. Open your Booked Opportunities report
3. Click **Export** → **Export Details**
4. Choose **CSV** format
5. Save and upload to the dashboard

## 📊 Expected CSV Format

Your Salesforce export should include:

**Required Columns:**
- Opportunity ID or Name
- Account Name
- Amount
- Close Date
- Stage

**Optional Columns:**
- Owner Name
- Opportunity Type
- Created Date
- Last Modified Date

The tool automatically detects column names from common Salesforce export formats.

### Sample Data

A sample CSV file is included: `sample_data.csv`

You can test the tool by uploading this sample file.

## 🎯 Dashboard Features

### Overview Tab
- Total opportunities count
- Closed Won opportunities
- Total revenue amount
- Recent upload activity
- Recent opportunities list with details

### Upload Tab
- Drag & drop CSV upload
- File validation
- Upload progress tracking
- Success/error messages
- Instructions for exporting from Salesforce

### All Opportunities Tab
- Complete table of all opportunities
- Real-time search across all fields
- Quick filtering
- Refresh button

### Upload History Tab
- Track all CSV uploads
- Upload timestamps
- Record counts
- Upload status

## 💡 Usage Tips

- **Regular Updates**: Upload new CSV exports daily or weekly to keep data current
- **Search**: Use the search box to quickly find opportunities by name, account, or owner
- **Historical Data**: The tool stores all uploads, so you can track changes over time
- **Multiple Uploads**: New uploads update existing records and add new ones

## 🔄 Next Steps - Future Enhancements

This is Version 1.0 with CSV upload functionality. Possible future additions:

1. **Automated Email Parsing** - Auto-import from scheduled Salesforce report emails
2. **Slack Notifications** - Alert channels when new opportunities are booked
3. **Email Notifications** - Send digest emails to team members
4. **Billing Exception Tracking** - Flag opportunities with billing setup issues
5. **Custom Reports** - Generate PDF/Excel reports
6. **Analytics Charts** - Visual trends and forecasting
7. **Multi-user Access** - Authentication and user management

## Project Structure

```
salesforce-opportunity-tool/
├── app.py                 # Flask web application
├── templates/            
│   └── index.html        # Dashboard interface
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
├── data/
│   └── opportunities.db  # SQLite database (auto-created)
├── uploads/              # Uploaded CSV files (auto-created)
├── venv/                 # Python virtual environment
├── sample_data.csv       # Sample CSV for testing
├── QUICKSTART.md         # Detailed getting started guide
└── README.md             # This file
```

## 🛠 Technology Stack

- **Backend**: Python 3.9, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite
- **Data Processing**: Pandas
- **File Upload**: Werkzeug

## 🔒 Security & Privacy

- All data stored locally on your machine
- No external API calls or data transmission
- CSV files saved in `uploads/` directory
- Database stored in `data/` directory
- No authentication required (local use only)

## 📞 Support

For issues or questions about using the tool, refer to:
- [QUICKSTART.md](QUICKSTART.md) - Detailed usage guide
- Check server terminal for error messages
- Verify CSV format matches expected structure
