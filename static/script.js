// Global state
let allOpportunities = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeUpload();
    loadDashboardData();
    loadRegionalData();
    loadOpportunities();
    loadUploadHistory();
    setupFilters();

    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadDashboardData();
        loadRegionalData();
    }, 30000);
});

// Tab switching
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.nav-item, .tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab
            button.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // Load data for specific tabs
            if (tabName === 'opportunities') {
                loadOpportunities();
            } else if (tabName === 'regions') {
                loadRegionalData();
            }
        });
    });
}

// Load dashboard statistics
function loadDashboardData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update KPI cards with new IDs
            const totalEl = document.getElementById('kpi-total');
            const holdbackEl = document.getElementById('kpi-holdback');
            const frameworkEl = document.getElementById('kpi-framework');
            const umbrellaEl = document.getElementById('kpi-umbrella');

            if (totalEl) totalEl.textContent = data.total_opportunities || '0';
            if (holdbackEl) holdbackEl.textContent = data.holdback_count || '0';
            if (frameworkEl) frameworkEl.textContent = data.framework_count || '0';
            if (umbrellaEl) umbrellaEl.textContent = data.umbrella_count || '0';

            // Load charts
            loadCharts();
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Load regional data
function loadRegionalData() {
    fetch('/api/region-summary')
        .then(response => response.json())
        .then(data => {
            displayRegionalTable(data.regions);
            displayExcludedByRegion(data.regions);
            updateFilterDropdowns(data);
        })
        .catch(error => console.error('Error loading regional data:', error));
}

// Display regional breakdown table
function displayRegionalTable(regions) {
    const tbody = document.getElementById('region-tbody');

    if (!regions || regions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No regional data available</td></tr>';
        return;
    }

    tbody.innerHTML = regions.map(region => `
        <tr>
            <td><strong>${region.region || 'Unknown'}</strong></td>
            <td>${region.total_projects}</td>
            <td>${region.holdback_count}</td>
            <td>${region.framework_count}</td>
            <td>${region.umbrella_count}</td>
            <td class="excluded-cell">${region.excluded_count}</td>
            <td>${formatCurrency(region.total_amount)}</td>
        </tr>
    `).join('');
}

// Display excluded projects by region
function displayExcludedByRegion(regions) {
    const container = document.getElementById('excluded-by-region');
    const excludedRegions = regions.filter(r => r.excluded_count > 0);

    if (excludedRegions.length === 0) {
        container.innerHTML = '<p class="success-message">✅ No projects excluded from billing!</p>';
        return;
    }

    container.innerHTML = `
        <div class="warning-box">
            <p><strong>⚠️ ${excludedRegions.length} region(s) have excluded projects:</strong></p>
            <ul>
                ${excludedRegions.map(r => `
                    <li><strong>${r.region}</strong>: ${r.excluded_count} project(s) excluded</li>
                `).join('')}
            </ul>
            <p class="hint">These projects require manual billing review before invoicing.</p>
        </div>
    `;
}

// Update filter dropdowns
function updateFilterDropdowns(data) {
    // Update region filter
    const regionFilter = document.getElementById('region-filter');
    const regions = new Set();
    data.regions.forEach(r => regions.add(r.region));

    regionFilter.innerHTML = '<option value="">All Regions</option>' +
        Array.from(regions).sort().map(r => `<option value="${r}">${r}</option>`).join('');

    // Update special term filter
    const termFilter = document.getElementById('special-term-filter');
    termFilter.innerHTML = '<option value="">All Special Terms</option>' +
        data.special_terms.map(t => `<option value="${t.term}">${t.term} (${t.count})</option>`).join('');
}

// Load and display opportunities
function loadOpportunities(filters = {}) {
    let url = '/api/opportunities?';
    if (filters.region) url += `region=${encodeURIComponent(filters.region)}&`;
    if (filters.special_term) url += `special_term=${encodeURIComponent(filters.special_term)}&`;
    if (filters.exclude_from_billing !== undefined) url += `exclude_from_billing=${filters.exclude_from_billing}&`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            allOpportunities = data;
            displayOpportunities(data);
        })
        .catch(error => console.error('Error loading opportunities:', error));
}

// Display opportunities in table
function displayOpportunities(opportunities) {
    const tbody = document.getElementById('opportunities-tbody');

    if (!opportunities || opportunities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">No projects found</td></tr>';
        return;
    }

    tbody.innerHTML = opportunities.map(opp => {
        const statusBadge = opp.exclude_from_billing === 1
            ? '<span class="badge badge-excluded">🔴 EXCLUDED</span>'
            : '<span class="badge badge-included">✅ INCLUDED</span>';

        return `
            <tr>
                <td title="${opp.name}">${truncate(opp.name, 40)}</td>
                <td>${opp.region || '-'}</td>
                <td><span class="term-badge term-${(opp.special_term || '').toLowerCase().replace(/\s+/g, '-')}">${opp.special_term || '-'}</span></td>
                <td>${opp.billing_frequency || '-'}</td>
                <td>${opp.project_manager || '-'}</td>
                <td>${opp.project_manager_2 || '-'}</td>
                <td>${formatDate(opp.close_date)}</td>
                <td>${formatCurrency(opp.amount)}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join('');
}

// Setup filters
function setupFilters() {
    const searchInput = document.getElementById('search-input');
    const regionFilter = document.getElementById('region-filter');
    const termFilter = document.getElementById('special-term-filter');
    const billingFilter = document.getElementById('billing-status-filter');
    const refreshButton = document.getElementById('refresh-button');
    const exportButton = document.getElementById('export-csv-button');

    const applyFilters = () => {
        const filters = {};
        if (regionFilter.value) filters.region = regionFilter.value;
        if (termFilter.value) filters.special_term = termFilter.value;
        if (billingFilter.value) filters.exclude_from_billing = billingFilter.value;

        loadOpportunities(filters);
    };

    regionFilter.addEventListener('change', applyFilters);
    termFilter.addEventListener('change', applyFilters);
    billingFilter.addEventListener('change', applyFilters);
    refreshButton.addEventListener('click', applyFilters);

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = allOpportunities.filter(opp =>
            (opp.name || '').toLowerCase().includes(searchTerm) ||
            (opp.account_name || '').toLowerCase().includes(searchTerm) ||
            (opp.project_manager || '').toLowerCase().includes(searchTerm) ||
            (opp.project_manager_2 || '').toLowerCase().includes(searchTerm)
        );
        displayOpportunities(filtered);
    });

    // Export CSV
    exportButton.addEventListener('click', exportToCSV);
}

// Export to CSV
function exportToCSV() {
    if (allOpportunities.length === 0) {
        alert('No data to export');
        return;
    }

    const headers = ['Project Name', 'Region', 'Special Term', 'Billing Frequency', 'PM 1', 'PM 2', 'Close Date', 'Amount', 'Excluded'];
    const rows = allOpportunities.map(opp => [
        opp.name,
        opp.region,
        opp.special_term,
        opp.billing_frequency,
        opp.project_manager,
        opp.project_manager_2,
        opp.close_date,
        opp.amount,
        opp.exclude_from_billing === 1 ? 'Yes' : 'No'
    ]);

    const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${cell || ''}"`).join(','))
        .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `psa-projects-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// File upload handling
function initializeUpload() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    uploadZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });
}

// Upload file to server
function uploadFile(file) {
    if (!file.name.endsWith('.csv')) {
        showUploadStatus('error', 'Please upload a CSV file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showUploadStatus('loading', 'Uploading...');

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showUploadStatus('error', data.error);
        } else {
            showUploadStatus('success',
                `✅ Success! Processed ${data.new + data.updated} projects (${data.new} new, ${data.updated} updated)`
            );
            // Refresh all data
            loadDashboardData();
            loadRegionalData();
            loadOpportunities();
            loadUploadHistory();
        }
    })
    .catch(error => {
        showUploadStatus('error', 'Upload failed: ' + error.message);
    });
}

// Show upload status
function showUploadStatus(type, message) {
    const statusDiv = document.getElementById('upload-status');
    statusDiv.className = `upload-status ${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
}

// Load upload history
function loadUploadHistory() {
    fetch('/api/upload-history')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('upload-history-list');
            if (data.length === 0) {
                container.innerHTML = '<p class="no-data">No upload history available</p>';
                return;
            }

            container.innerHTML = data.map(item => `
                <div class="history-item">
                    <div class="history-icon">📄</div>
                    <div class="history-content">
                        <div class="history-filename">${item.filename}</div>
                        <div class="history-meta">
                            ${formatDateTime(item.upload_date)} • ${item.records_count} records • ${item.status}
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading upload history:', error));
}

// Utility functions
function formatCurrency(amount) {
    if (!amount || amount === 0) return '-';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return dateString;
    }
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateString;
    }
}

function truncate(str, maxLength) {
    if (!str) return '-';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}
