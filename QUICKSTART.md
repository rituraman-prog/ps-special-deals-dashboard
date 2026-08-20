# Quick Start Guide

## 🚀 Getting Started

Your CSV Upload Tool is ready! Follow these steps to start using it.

### Step 1: Start the Server

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python app.py
```

You should see:
```
🚀 Salesforce Opportunity Dashboard
📊 Server starting at: http://localhost:5001
```

### Step 2: Open in Browser

Open your web browser and go to:
```
http://localhost:5001
```

### Step 3: Export Data from Salesforce

1. Log into Salesforce: https://org62.lightning.force.com
2. Navigate to your Booked Opportunities report
3. Click **Export** or the export button (usually looks like ⬇️)
4. Select **Export Details**
5. Choose **CSV** format
6. Save the file to your computer

### Step 4: Upload to Dashboard

1. In the dashboard, click the **Upload Data** tab
2. Either:
   - Drag and drop your CSV file into the upload area
   - Click **Choose File** to browse and select
3. Wait for processing (usually takes 2-5 seconds)
4. You'll see a success message with the number of records processed

### Step 5: View Your Data

- **Dashboard Tab**: See overview statistics and recent opportunities
- **All Opportunities Tab**: Browse and search all uploaded data
- **Upload History Tab**: Track your uploads

## 📊 Expected CSV Format

Your Salesforce export should include these columns (names may vary):

**Required:**
- Opportunity ID or Name
- Account Name
- Amount
- Close Date
- Stage

**Optional (but recommended):**
- Owner Name
- Opportunity Type
- Created Date
- Last Modified Date

### Example CSV Structure:

```csv
Opportunity ID,Opportunity Name,Account Name,Amount,Close Date,Stage,Owner Name
006xx000001234,Acme Corp Deal,Acme Corporation,250000,2026-08-15,Closed Won,John Smith
006xx000005678,Global Services,Global Inc,175000,2026-08-10,Closed Won,Jane Doe
```

## ✨ Features

### Dashboard
- Total opportunities count
- Closed Won count
- Total revenue amount
- Recent upload activity
- Recent opportunities list

### Upload Data
- Drag & drop CSV upload
- Automatic column detection
- Handles various Salesforce export formats
- Updates existing records
- Shows upload progress and results

### All Opportunities
- Full table view of all opportunities
- Search by name, account, owner, or stage
- Real-time filtering
- Sortable columns

### Upload History
- Track all uploads
- See upload timestamps
- View record counts
- Monitor status

## 🔍 Troubleshooting

### "Could not detect required columns"
- Make sure your CSV includes: Opportunity ID/Name, Account, Amount, Close Date, Stage
- Check that your Salesforce report includes these fields
- Try re-exporting with all columns selected

### "No opportunities found"
- Make sure you've uploaded a CSV file first
- Check that your CSV contains data rows (not just headers)
- Verify the Stage field contains values

### Server won't start
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Check that port 5000 is not in use
- Try: `python app.py` again

### Can't access http://localhost:5001
- Verify the server is running (check terminal)
- Try: http://127.0.0.1:5000 instead
- Check firewall settings

## 📁 Data Storage

All data is stored locally in:
```
~/salesforce-opportunity-tool/data/opportunities.db
```

This is a SQLite database file that stores:
- All uploaded opportunities
- Upload history
- Configuration settings

## 🔄 Updating Data

To refresh your data:
1. Export a new CSV from Salesforce
2. Upload it through the dashboard
3. Existing opportunities will be updated
4. New opportunities will be added

## 🎯 Next Steps

Now that your basic tool is working, you can:

1. **Set up automated uploads** (email parsing)
2. **Add Slack notifications**
3. **Create custom reports**
4. **Add billing exception tracking**
5. **Export data for analysis**

Want to add any of these features? Let me know!

## 💡 Tips

- Upload data regularly (daily or weekly) to keep the dashboard current
- Use the search function to quickly find specific opportunities
- Check upload history to track data freshness
- Bookmark http://localhost:5001 for quick access

## 🆘 Need Help?

If you run into issues:
1. Check the terminal where the server is running for error messages
2. Try refreshing the browser page
3. Restart the server
4. Check that your CSV file is properly formatted

---

**Ready to go!** 🎉 Start the server and upload your first CSV file!
