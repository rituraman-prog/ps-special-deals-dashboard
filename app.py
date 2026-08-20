"""
Salesforce Opportunity Dashboard - CSV Upload Tool
Main Flask application
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from db_helper import get_db_connection, init_database

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['DATABASE'] = 'data/opportunities.db'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    """Initialize database (SQLite or PostgreSQL)"""
    # Use the db_helper which handles both SQLite and PostgreSQL
    init_database()
    return

    # OLD CODE BELOW - keeping for reference but not used
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Create opportunities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            name TEXT,
            account_name TEXT,
            amount REAL,
            close_date TEXT,
            stage_name TEXT,
            owner_name TEXT,
            opportunity_type TEXT,
            created_date TEXT,
            last_modified_date TEXT,
            upload_date TEXT,
            upload_filename TEXT,
            project_manager TEXT,
            project_manager_2 TEXT,
            opportunity_owner TEXT,
            region TEXT,
            subregion TEXT,
            special_term TEXT,
            billing_frequency TEXT,
            account_number TEXT,
            amount_currency TEXT,
            opportunity_stage TEXT,
            billings_currency TEXT,
            billings REAL,
            actual_remaining_currency TEXT,
            actual_remaining REAL,
            invoiced_currency TEXT,
            invoiced REAL,
            po_number TEXT,
            exclude_from_billing INTEGER
        )
    ''')

    # Create uploads history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TEXT,
            records_count INTEGER,
            status TEXT
        )
    ''')

    # Create notifications config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slack_webhook_url TEXT,
            email_enabled INTEGER DEFAULT 0,
            email_recipients TEXT,
            notify_on_new_opp INTEGER DEFAULT 1,
            notify_on_exceptions INTEGER DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()


def get_db():
    """Get database connection (SQLite or PostgreSQL)"""
    return get_db_connection()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)

        # Parse CSV with encoding detection
        df = read_csv_with_encoding(filepath)

        # Process and store data
        result = process_csv(df, saved_filename)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def read_csv_with_encoding(filepath):
    """
    Read CSV file with automatic encoding detection.
    Tries multiple common encodings used by Salesforce exports.
    """
    # Common encodings for Salesforce exports
    encodings = [
        'utf-8',           # Default
        'utf-8-sig',       # UTF-8 with BOM
        'latin-1',         # ISO-8859-1
        'windows-1252',    # Windows encoding (most common for Salesforce)
        'cp1252',          # Another Windows variant
        'iso-8859-1',      # Latin alphabet
    ]

    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            print(f"✅ Successfully read CSV with encoding: {encoding}")
            return df
        except UnicodeDecodeError as e:
            last_error = e
            print(f"⚠️ Failed with {encoding}, trying next encoding...")
            continue
        except Exception as e:
            # Other errors should be raised immediately
            raise e

    # If all encodings failed, raise the last error
    raise UnicodeDecodeError(
        'multiple',
        b'',
        0,
        1,
        f'Could not decode CSV with any of these encodings: {", ".join(encodings)}. Last error: {last_error}'
    )


def process_csv(df, filename):
    """Process uploaded CSV and store in database"""
    conn = get_db()
    cursor = conn.cursor()

    # Detect column names (handle variations in Salesforce exports)
    column_mapping = detect_columns(df)

    if not column_mapping:
        conn.close()
        return {'error': 'Could not detect required columns in CSV. Expected: Opportunity ID/Name, Account, Amount, Close Date, Stage'}

    new_count = 0
    updated_count = 0
    upload_date = datetime.now().isoformat()

    for _, row in df.iterrows():
        try:
            # Extract data using detected column mapping
            # Handle PSA format vs Standard format
            # PSA format is detected by presence of 'special_term' or 'psa project' name
            if 'special_term' in column_mapping or 'opp_name' in column_mapping:
                # PSA Projects format
                name = str(row.get(column_mapping.get('name', 'Name'), ''))  # Project name
                opp_name = str(row.get(column_mapping.get('opp_name', ''), ''))  # Opportunity name

                # Generate ID from project name if not provided
                opp_id = str(row.get(column_mapping.get('id', ''), ''))
                if not opp_id or opp_id == 'nan' or opp_id == '':
                    # Use project name hash as ID
                    import hashlib
                    opp_id = f"PSA_{hashlib.md5(name.encode()).hexdigest()[:12]}"

                # Use opp_name if available, otherwise use account_number or empty
                account = opp_name if opp_name else str(row.get(column_mapping.get('account_number', ''), ''))
                amount = parse_amount(row.get(column_mapping.get('amount', 'Opportunity Amount'), 0))
                close_date = str(row.get(column_mapping.get('close_date', 'Close Date'), ''))
                stage = str(row.get(column_mapping.get('opportunity_stage', 'Stage'), ''))
                owner = str(row.get(column_mapping.get('opp_owner', 'Owner'), ''))
                opp_type = str(row.get(column_mapping.get('billing_frequency', 'Type'), ''))
                created = ''
                modified = ''

                # Extract new fields
                pm1 = str(row.get(column_mapping.get('pm1', ''), ''))
                pm2 = str(row.get(column_mapping.get('pm2', ''), ''))
                # Try both opportunity owner columns
                opportunity_owner = str(row.get(column_mapping.get('opp_owner', ''), ''))
                if not opportunity_owner:
                    opportunity_owner = str(row.get(column_mapping.get('opportunity_owner_alt', ''), ''))
                region = str(row.get(column_mapping.get('region', ''), ''))
                subregion = str(row.get(column_mapping.get('subregion', ''), ''))
                special_term = str(row.get(column_mapping.get('special_term', ''), ''))
                billing_frequency = str(row.get(column_mapping.get('billing_frequency', ''), ''))
                account_number = str(row.get(column_mapping.get('account_number', ''), ''))
                amount_currency = str(row.get(column_mapping.get('amount_currency', ''), ''))
                opportunity_stage = str(row.get(column_mapping.get('opportunity_stage', ''), ''))
                billings_currency = str(row.get(column_mapping.get('billings_currency', ''), ''))
                billings = parse_amount(row.get(column_mapping.get('billings', ''), 0))
                actual_remaining_currency = str(row.get(column_mapping.get('actual_remaining_currency', ''), ''))
                actual_remaining = parse_amount(row.get(column_mapping.get('actual_remaining', ''), 0))
                invoiced_currency = str(row.get(column_mapping.get('invoiced_currency', ''), ''))
                invoiced = parse_amount(row.get(column_mapping.get('invoiced', ''), 0))
                po_number = str(row.get(column_mapping.get('po_number', ''), ''))
                exclude_from_billing = int(row.get(column_mapping.get('exclude_from_billing', ''), 0))
            else:
                # Standard Opportunities format
                opp_id = str(row.get(column_mapping.get('id', 'ID'), ''))
                if not opp_id or opp_id == 'nan':
                    opp_id = f"TEMP_{datetime.now().timestamp()}_{_}"

                name = str(row.get(column_mapping.get('name', 'Name'), ''))
                account = str(row.get(column_mapping.get('account', 'Account Name'), ''))
                amount = parse_amount(row.get(column_mapping.get('amount', 'Amount'), 0))
                close_date = str(row.get(column_mapping.get('close_date', 'Close Date'), ''))
                stage = str(row.get(column_mapping.get('stage', 'Stage'), ''))
                owner = str(row.get(column_mapping.get('owner', 'Owner'), ''))
                opp_type = str(row.get(column_mapping.get('type', 'Type'), ''))
                created = str(row.get(column_mapping.get('created_date', 'Created Date'), ''))
                modified = str(row.get(column_mapping.get('modified_date', 'Last Modified Date'), ''))

                # Set defaults for fields not in standard format
                pm1 = ''
                pm2 = ''
                opportunity_owner = owner
                region = ''
                subregion = ''
                special_term = ''
                billing_frequency = opp_type
                account_number = ''
                amount_currency = ''
                opportunity_stage = stage
                billings_currency = ''
                billings = 0.0
                actual_remaining_currency = ''
                actual_remaining = 0.0
                invoiced_currency = ''
                invoiced = 0.0
                po_number = ''
                exclude_from_billing = 0

            # Check if opportunity exists
            cursor.execute('SELECT id FROM opportunities WHERE id = ?', (opp_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing
                cursor.execute('''
                    UPDATE opportunities
                    SET name=?, account_name=?, amount=?, close_date=?, stage_name=?,
                        owner_name=?, opportunity_type=?, created_date=?, last_modified_date=?,
                        upload_date=?, upload_filename=?, project_manager=?, project_manager_2=?,
                        opportunity_owner=?, region=?, subregion=?, special_term=?, billing_frequency=?,
                        account_number=?, amount_currency=?, opportunity_stage=?, billings_currency=?,
                        billings=?, actual_remaining_currency=?, actual_remaining=?, invoiced_currency=?,
                        invoiced=?, po_number=?, exclude_from_billing=?
                    WHERE id=?
                ''', (name, account, amount, close_date, stage, owner, opp_type,
                      created, modified, upload_date, filename, pm1, pm2,
                      opportunity_owner, region, subregion, special_term, billing_frequency,
                      account_number, amount_currency, opportunity_stage, billings_currency,
                      billings, actual_remaining_currency, actual_remaining, invoiced_currency,
                      invoiced, po_number, exclude_from_billing, opp_id))
                updated_count += 1
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO opportunities
                    (id, name, account_name, amount, close_date, stage_name, owner_name,
                     opportunity_type, created_date, last_modified_date, upload_date, upload_filename,
                     project_manager, project_manager_2, opportunity_owner, region, subregion,
                     special_term, billing_frequency, account_number, amount_currency, opportunity_stage,
                     billings_currency, billings, actual_remaining_currency, actual_remaining,
                     invoiced_currency, invoiced, po_number, exclude_from_billing)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (opp_id, name, account, amount, close_date, stage, owner, opp_type,
                      created, modified, upload_date, filename, pm1, pm2,
                      opportunity_owner, region, subregion, special_term, billing_frequency,
                      account_number, amount_currency, opportunity_stage, billings_currency,
                      billings, actual_remaining_currency, actual_remaining, invoiced_currency,
                      invoiced, po_number, exclude_from_billing))
                new_count += 1

        except Exception as e:
            print(f"Error processing row {_}: {e}")
            continue

    # Record upload history
    cursor.execute('''
        INSERT INTO upload_history (filename, upload_date, records_count, status)
        VALUES (?, ?, ?, ?)
    ''', (filename, upload_date, new_count + updated_count, 'success'))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'message': f'Processed {new_count + updated_count} opportunities',
        'new': new_count,
        'updated': updated_count,
        'filename': filename
    }


def detect_columns(df):
    """Detect column names in CSV (handle variations including PSA Projects format)"""
    mapping = {}
    columns_lower = {col.lower(): col for col in df.columns}

    # Debug: print available columns
    print(f"DEBUG: First 5 columns: {list(df.columns)[:5]}")
    print(f"DEBUG: First 5 lowercase keys: {list(columns_lower.keys())[:5]}")

    # PSA Projects format patterns (prioritize these)
    psa_patterns = {
        'name': ['psa project: project name'],
        'opp_name': ['opportunity: opportunity name'],
        'special_term': ['special term'],
        'billing_frequency': ['opportunity: quote billing frequency', 'quote billing frequency'],
        'pm1': ['project manager'],
        'pm2': ['project manager 2 (contact)', 'project manager 2'],
        'opp_owner': ['opportunity: opportunity owner'],
        'opportunity_owner_alt': ['opportunity owner'],
        'region': ['region'],
        'subregion': ['subregion'],
        'account_number': ['account number'],
        'amount_currency': ['opportunity amount currency'],
        'amount': ['opportunity amount'],
        'close_date': ['opportunity close date'],
        'opportunity_stage': ['opportunity stage'],
        'billings_currency': ['billings currency'],
        'billings': ['billings'],
        'actual_remaining_currency': ['project: actual amount remaining currency'],
        'actual_remaining': ['project: actual amount remaining'],
        'invoiced_currency': ['invoiced currency'],
        'invoiced': ['invoiced'],
        'po_number': ['po number'],
        'exclude_from_billing': ['exclude from billing']
    }

    # Standard Opportunities format patterns
    standard_patterns = {
        'id': ['opportunity id', 'opp id', 'id', 'opportunityid'],
        'name': ['opportunity name', 'opp name', 'name', 'opportunityname'],
        'account': ['account name', 'account', 'accountname'],
        'amount': ['amount', 'opportunity amount'],
        'close_date': ['close date', 'closedate', 'closed date'],
        'stage': ['stage', 'stage name', 'stagename', 'opportunity stage'],
        'owner': ['owner', 'owner name', 'ownername', 'opportunity owner'],
        'type': ['type', 'opportunity type', 'opp type'],
        'created_date': ['created date', 'createddate', 'created'],
        'modified_date': ['last modified date', 'lastmodifieddate', 'modified date', 'modified']
    }

    # First, try to detect PSA format
    is_psa_format = False
    for key, variations in psa_patterns.items():
        for variation in variations:
            if variation in columns_lower:
                mapping[key] = columns_lower[variation]
                is_psa_format = True
                break

    # If PSA format detected, return PSA mapping
    if is_psa_format:
        print("✅ Detected PSA Projects format")
        print(f"DEBUG: PSA mapping: {mapping}")
        # For PSA format, we need at least project name
        if 'name' in mapping:
            return mapping
        else:
            return None

    # Otherwise, try standard format
    for key, variations in standard_patterns.items():
        for variation in variations:
            if variation in columns_lower:
                mapping[key] = columns_lower[variation]
                break

    # Return mapping if we found at least name or id
    if mapping and ('name' in mapping or 'id' in mapping):
        print("✅ Detected Standard Opportunities format")
        return mapping

    return None


def parse_amount(value):
    """Parse amount value (handle currency formatting)"""
    if pd.isna(value):
        return 0.0
    try:
        # Remove currency symbols and commas
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').strip()
        return float(value)
    except:
        return 0.0


@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    """Get all opportunities with enhanced filtering"""
    conn = get_db()
    cursor = conn.cursor()

    # Get filter parameters
    stage = request.args.get('stage', None)
    region = request.args.get('region', None)
    special_term = request.args.get('special_term', None)
    exclude_from_billing = request.args.get('exclude_from_billing', None)
    days = request.args.get('days', None)

    query = 'SELECT * FROM opportunities'
    params = []
    conditions = []

    if stage:
        conditions.append('stage_name = ?')
        params.append(stage)

    if region:
        conditions.append('region = ?')
        params.append(region)

    if special_term:
        conditions.append('special_term = ?')
        params.append(special_term)

    if exclude_from_billing is not None:
        conditions.append('exclude_from_billing = ?')
        params.append(int(exclude_from_billing))

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY close_date DESC'

    if days:
        query += ' LIMIT ?'
        params.append(int(days))

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    opportunities = []
    for row in rows:
        opportunities.append({
            'id': row['id'],
            'name': row['name'],
            'account_name': row['account_name'],
            'amount': row['amount'],
            'close_date': row['close_date'],
            'stage_name': row['stage_name'],
            'owner_name': row['owner_name'],
            'opportunity_type': row['opportunity_type'],
            'created_date': row['created_date'],
            'last_modified_date': row['last_modified_date'],
            'project_manager': row['project_manager'],
            'project_manager_2': row['project_manager_2'],
            'opportunity_owner': row['opportunity_owner'],
            'region': row['region'],
            'subregion': row['subregion'],
            'special_term': row['special_term'],
            'billing_frequency': row['billing_frequency'],
            'account_number': row['account_number'],
            'amount_currency': row['amount_currency'],
            'opportunity_stage': row['opportunity_stage'],
            'billings_currency': row['billings_currency'],
            'billings': row['billings'],
            'actual_remaining_currency': row['actual_remaining_currency'],
            'actual_remaining': row['actual_remaining'],
            'invoiced_currency': row['invoiced_currency'],
            'invoiced': row['invoiced'],
            'po_number': row['po_number'],
            'exclude_from_billing': row['exclude_from_billing']
        })

    return jsonify(opportunities)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()

    # Total opportunities
    cursor.execute("SELECT COUNT(*) as count FROM opportunities")
    total = cursor.fetchone()['count']

    # Closed Won opportunities
    cursor.execute("SELECT COUNT(*) as count FROM opportunities WHERE stage_name LIKE '%Closed%Won%'")
    closed_won = cursor.fetchone()['count']

    # Total amount
    cursor.execute("SELECT SUM(amount) as total FROM opportunities WHERE stage_name LIKE '%Closed%Won%'")
    total_amount = cursor.fetchone()['total'] or 0

    # Recent uploads
    cursor.execute("SELECT COUNT(*) as count FROM upload_history WHERE date(upload_date) >= date('now', '-7 days')")
    recent_uploads = cursor.fetchone()['count']

    # Count by special term
    cursor.execute("SELECT COUNT(*) as count FROM opportunities WHERE special_term = 'Holdback'")
    holdback_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM opportunities WHERE special_term = 'Framework'")
    framework_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM opportunities WHERE special_term = 'Umbrella'")
    umbrella_count = cursor.fetchone()['count']

    # Count excluded from billing
    cursor.execute("SELECT COUNT(*) as count FROM opportunities WHERE exclude_from_billing = 1")
    excluded_count = cursor.fetchone()['count']

    conn.close()

    return jsonify({
        'total_opportunities': total,
        'closed_won': closed_won,
        'total_amount': total_amount,
        'recent_uploads': recent_uploads,
        'holdback_count': holdback_count,
        'framework_count': framework_count,
        'umbrella_count': umbrella_count,
        'excluded_count': excluded_count
    })


@app.route('/api/upload-history', methods=['GET'])
def get_upload_history():
    """Get upload history"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM upload_history ORDER BY upload_date DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            'id': row['id'],
            'filename': row['filename'],
            'upload_date': row['upload_date'],
            'records_count': row['records_count'],
            'status': row['status']
        })

    return jsonify(history)


@app.route('/api/region-summary', methods=['GET'])
def get_region_summary():
    """Get regional breakdown statistics"""
    conn = get_db()
    cursor = conn.cursor()

    # Get all regions with statistics
    cursor.execute('''
        SELECT
            region,
            COUNT(*) as total_projects,
            SUM(CASE WHEN special_term = 'Holdback' THEN 1 ELSE 0 END) as holdback_count,
            SUM(CASE WHEN special_term = 'Framework' THEN 1 ELSE 0 END) as framework_count,
            SUM(CASE WHEN special_term = 'Umbrella' THEN 1 ELSE 0 END) as umbrella_count,
            SUM(CASE WHEN exclude_from_billing = 1 THEN 1 ELSE 0 END) as excluded_count,
            SUM(amount) as total_amount
        FROM opportunities
        WHERE region IS NOT NULL AND region != ''
        GROUP BY region
        ORDER BY total_projects DESC
    ''')

    regions = []
    for row in cursor.fetchall():
        region_data = {
            'region': row['region'],
            'total': row['total_projects'],
            'total_projects': row['total_projects'],
            'holdback_count': row['holdback_count'],
            'framework_count': row['framework_count'],
            'umbrella_count': row['umbrella_count'],
            'excluded_count': row['excluded_count'],
            'total_amount': row['total_amount'] or 0
        }
        regions.append(region_data)

    # Get special terms summary
    cursor.execute('''
        SELECT
            special_term,
            COUNT(*) as count
        FROM opportunities
        WHERE special_term IS NOT NULL AND special_term != ''
        GROUP BY special_term
        ORDER BY count DESC
    ''')

    special_terms = []
    for row in cursor.fetchall():
        special_terms.append({
            'term': row['special_term'],
            'count': row['count']
        })

    # Get billing frequency breakdown
    cursor.execute('''
        SELECT
            billing_frequency,
            COUNT(*) as count
        FROM opportunities
        WHERE billing_frequency IS NOT NULL AND billing_frequency != ''
        GROUP BY billing_frequency
        ORDER BY count DESC
    ''')

    billing_frequencies = []
    for row in cursor.fetchall():
        billing_frequencies.append({
            'frequency': row['billing_frequency'],
            'count': row['count']
        })

    # Get special terms breakdown by region (for combined chart)
    cursor.execute('''
        SELECT
            region,
            special_term,
            COUNT(*) as count
        FROM opportunities
        WHERE region IS NOT NULL AND region != ''
        AND special_term IS NOT NULL AND special_term != ''
        GROUP BY region, special_term
        ORDER BY region, count DESC
    ''')

    region_term_breakdown = {}
    for row in cursor.fetchall():
        region = row['region']
        special_term = row['special_term']
        count = row['count']

        if region not in region_term_breakdown:
            region_term_breakdown[region] = {}
        region_term_breakdown[region][special_term] = count

        # Also add to the regions array for easier access
        for region_obj in regions:
            if region_obj['region'] == region:
                # Convert special term to a safe key name
                safe_key = special_term.lower().replace(' ', '_').replace('/', '_').replace('+', 'plus').replace('(', '').replace(')', '')
                region_obj[f'{safe_key}_count'] = count
                break

    conn.close()

    return jsonify({
        'regions': regions,
        'special_terms': special_terms,
        'billing_frequencies': billing_frequencies,
        'region_term_breakdown': region_term_breakdown
    })


# Initialize database on import (for production)
init_db()

if __name__ == '__main__':
    # Local development
    print("="*80)
    print("🚀 Salesforce Opportunity Dashboard")
    print("="*80)
    print("📊 Server starting at: http://localhost:5001")
    print("📁 Upload CSV files from Salesforce to get started!")
    print("="*80)

    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(debug=debug, host='0.0.0.0', port=port)
