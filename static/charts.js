// Chart management for dashboard
let regionChart = null;
let specialTermsChart = null;

// Load and create all charts
function loadCharts() {
    fetch('/api/region-summary')
        .then(response => response.json())
        .then(data => {
            console.log('Chart data loaded:', data);
            createRegionChart(data.regions);
            createSpecialTermsChart(data.special_terms);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
        });
}

// Create elegant region bar chart
function createRegionChart(regions) {
    const canvas = document.getElementById('regionChart');
    if (!canvas) {
        console.error('Region chart canvas not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Cannot get canvas context');
        return;
    }

    // Destroy existing chart
    if (regionChart) {
        regionChart.destroy();
    }

    // Get top 10 regions
    const topRegions = regions.slice(0, 10);

    console.log('Creating region chart with', topRegions.length, 'regions');

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.9)');
    gradient.addColorStop(1, 'rgba(118, 75, 162, 0.7)');

    regionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topRegions.map(r => r.region || 'Unknown'),
            datasets: [{
                label: 'Number of Projects',
                data: topRegions.map(r => r.total_projects),
                backgroundColor: gradient,
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 16,
                    titleFont: {
                        size: 15,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 14
                    },
                    borderColor: 'rgba(102, 126, 234, 0.5)',
                    borderWidth: 2,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return `Projects: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 12,
                            weight: '600'
                        },
                        color: '#475569',
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        color: '#64748b',
                        precision: 0,
                        padding: 10
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    console.log('Region chart created successfully');
}

// Create elegant special terms doughnut chart
function createSpecialTermsChart(terms) {
    const canvas = document.getElementById('specialTermsChart');
    if (!canvas) {
        console.error('Special terms chart canvas not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Cannot get canvas context');
        return;
    }

    // Destroy existing chart
    if (specialTermsChart) {
        specialTermsChart.destroy();
    }

    console.log('Creating special terms chart with', terms.length, 'terms');

    // Beautiful color palette
    const colors = [
        { bg: 'rgba(240, 147, 251, 0.9)', border: 'rgba(240, 147, 251, 1)' },   // Pink - Holdback
        { bg: 'rgba(79, 172, 254, 0.9)', border: 'rgba(79, 172, 254, 1)' },     // Blue - Framework
        { bg: 'rgba(67, 233, 123, 0.9)', border: 'rgba(67, 233, 123, 1)' },     // Green - Umbrella
        { bg: 'rgba(255, 184, 77, 0.9)', border: 'rgba(255, 184, 77, 1)' },     // Orange
        { bg: 'rgba(153, 102, 255, 0.9)', border: 'rgba(153, 102, 255, 1)' },   // Purple
        { bg: 'rgba(255, 99, 132, 0.9)', border: 'rgba(255, 99, 132, 1)' },     // Red
        { bg: 'rgba(54, 162, 235, 0.9)', border: 'rgba(54, 162, 235, 1)' },     // Light Blue
        { bg: 'rgba(255, 206, 86, 0.9)', border: 'rgba(255, 206, 86, 1)' }      // Yellow
    ];

    const total = terms.reduce((sum, t) => sum + t.count, 0);

    specialTermsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: terms.map(t => t.term || 'Other'),
            datasets: [{
                data: terms.map(t => t.count),
                backgroundColor: terms.map((_, i) => colors[i % colors.length].bg),
                borderColor: terms.map((_, i) => colors[i % colors.length].border),
                borderWidth: 3,
                hoverOffset: 15,
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 13,
                            weight: '600',
                            family: 'Inter, sans-serif'
                        },
                        color: '#475569',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        boxWidth: 12,
                        boxHeight: 12
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 16,
                    titleFont: {
                        size: 15,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 14
                    },
                    borderColor: 'rgba(102, 126, 234, 0.5)',
                    borderWidth: 2,
                    displayColors: true,
                    boxWidth: 12,
                    boxHeight: 12,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return [
                                `Projects: ${value}`,
                                `Percentage: ${percentage}%`
                            ];
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1200,
                easing: 'easeInOutQuart'
            }
        }
    });

    console.log('Special terms chart created successfully');
}

// Export functions
window.loadCharts = loadCharts;
window.createRegionChart = createRegionChart;
window.createSpecialTermsChart = createSpecialTermsChart;
