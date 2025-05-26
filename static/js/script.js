$(document).ready(function() {
    // Initialize dashboard
    initDashboard();
    
    // Refresh button click handler
    $('#refresh-btn').click(function() {
        initDashboard();
    });
    
    // Time period change handler
    $('#time-period').change(function() {
        initDashboard();
    });
});

function initDashboard() {
    const period = $('#time-period').val();
    
    // Simulate loading data based on selected period
    simulateData(period);
    
    // Initialize sparklines
    initSparklines();
    
    // Initialize charts  -revisit later
    //initCharts();
}

function simulateData(period) {
    // This would normally come from an API
    // For demo, we'll just generate random data
    
    // Base values based on period
    let revenueBase, retailersBase, customersBase, conversionBase, avgOrderBase;
    
    switch(period) {
        case 'today':
            revenueBase = 5000 + Math.random() * 3000;
            retailersBase = 100 + Math.random() * 50;
            customersBase = 100 + Math.random() * 50;
            conversionBase = 2.5 + Math.random() * 2;
            avgOrderBase = 75 + Math.random() * 30;
            break;
        case 'week':
            revenueBase = 24000 + Math.random() * 10000;
            retailersBase = 1800 + Math.random() * 500;
            customersBase = 1800 + Math.random() * 500;
            conversionBase = 3.0 + Math.random() * 1.5;
            avgOrderBase = 85 + Math.random() * 20;
            break;
        case 'month':
            revenueBase = 100000 + Math.random() * 50000;
            retailersBase = 8000 + Math.random() * 3000;
            customersBase = 8000 + Math.random() * 3000;
            conversionBase = 3.5 + Math.random() * 1.5;
            avgOrderBase = 90 + Math.random() * 25;
            break;
        case 'quarter':
            revenueBase = 300000 + Math.random() * 150000;
            retailersBase = 25000 + Math.random() * 10000;
            customersBase = 25000 + Math.random() * 10000;
            conversionBase = 3.8 + Math.random() * 1.2;
            avgOrderBase = 95 + Math.random() * 30;
            break;
        case 'year':
            revenueBase = 1200000 + Math.random() * 600000;
            retailersBase = 100000 + Math.random() * 50000;
            customersBase = 100000 + Math.random() * 50000;
            conversionBase = 4.0 + Math.random() * 1.0;
            avgOrderBase = 100 + Math.random() * 40;
            break;
    }
    
    // Format numbers
    const revenue = Math.round(revenueBase).toLocaleString();
    const retailers = Math.round(retailersBase).toLocaleString();
    const customers = Math.round(customersBase).toLocaleString();
    const conversion = (conversionBase).toFixed(1) + '%';
    const avgOrder = '€' + (avgOrderBase).toFixed(2);
    
    // Generate random changes (positive or negative)
    const revenueChange = (Math.random() > 0.2 ? '+' : '-') + (Math.random() * 15).toFixed(1) + '%';
    const retailersChange = (Math.random() > 0.3 ? '+' : '-') + (Math.random() * 10).toFixed(1) + '%';
    const customersChange = (Math.random() > 0.3 ? '+' : '-') + (Math.random() * 10).toFixed(1) + '%';
    const conversionChange = (Math.random() > 0.4 ? '+' : '-') + (Math.random() * 2).toFixed(1) + '%';
    const avgOrderChange = (Math.random() > 0.2 ? '+' : '-') + (Math.random() * 8).toFixed(1) + '%';
    
    // Update KPI values
    $('#revenue').text('€' + revenue);
    $('#retailers').text(retailers);
    $('#customers').text(customers);
    $('#conversion').text(conversion);
    $('#avg-order').text(avgOrder);
    
    // Update change indicators
    updateChangeIndicator('#revenue-change', revenueChange);
    updateChangeIndicator('#retailers-change', retailersChange);
    updateChangeIndicator('#customers-change', customersChange);
    updateChangeIndicator('#conversion-change', conversionChange);
    updateChangeIndicator('#avg-order-change', avgOrderChange);
}

function updateChangeIndicator(selector, change) {
    const isPositive = change.startsWith('+');
    const element = $(selector);
    
    element.html((isPositive ? 
        '<i class="fas fa-arrow-up"></i> ' : 
        '<i class="fas fa-arrow-down"></i> ') + 
        change.substring(1) + ' vs last period');
    
    element.removeClass('positive negative')
           .addClass(isPositive ? 'positive' : 'negative');
}

function initSparklines() {
    // Generate random sparkline data
    const generateSparklineData = (points, min, max) => {
        return Array.from({length: points}, () => 
            Math.floor(Math.random() * (max - min + 1)) + min);
    };
    
    // Initialize sparklines for each KPI
    $('#revenue-trend').sparkline(generateSparklineData(10, 50, 100), {
        type: 'line',
        width: '100%',
        height: '120px',
        lineColor: '#2ecc71',
        fillColor: 'rgba(46, 204, 113, 0.2)',
        lineWidth: 2,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    });
    
    $('#customers-trend').sparkline(generateSparklineData(10, 30, 80), {
        type: 'line',
        width: '100%',
        height: '40px',
        lineColor: '#3498db',
        fillColor: 'rgba(52, 152, 219, 0.2)',
        lineWidth: 2,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    });
 
    $('#conversion-trend').sparkline(generateSparklineData(10, 20, 50), {
        type: 'line',
        width: '100%',
        height: '40px',
        lineColor: '#3498db',
        fillColor: 'rgba(52, 152, 219, 0.2)',
        lineWidth: 2,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    });

    $('#retailers-trend').sparkline(generateSparklineData(10, 30, 80), {
        type: 'line',
        width: '100%',
        height: '40px',
        lineColor: '#f39c12',
        fillColor: 'rgba(243, 156, 18, 0.2)',
        lineWidth: 2,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    });

    $('#avg-order-trend').sparkline(generateSparklineData(10, 60, 90), {
        type: 'line',
        width: '100%',
        height: '40px',
        lineColor: '#f39c12',
        fillColor: 'rgba(243, 156, 18, 0.2)',
        lineWidth: 2,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    });
}

function initCharts() {
    // Simple bar chart implementation using divs (for demo purposes)
    // In a real app, you might use a proper charting library
    
    // Revenue chart
    const revenueData = [
        { month: 'Jan', value: 120 },
        { month: 'Feb', value: 150 },
        { month: 'Mar', value: 180 },
        { month: 'Apr', value: 90 },
        { month: 'May', value: 160 },
        { month: 'Jun', value: 200 }
    ];
    
    renderBarChart('#revenue-chart', revenueData, '#2ecc71');
    
    // Acquisition chart
    const acquisitionData = [
        { source: 'Organic', value: 45 },
        { source: 'Direct', value: 25 },
        { source: 'Social', value: 15 },
        { source: 'Email', value: 10 },
        { source: 'Referral', value: 5 }
    ];
    
    renderBarChart('#acquisition-chart', acquisitionData, '#3498db', true);
}

function renderBarChart(container, data, color, isHorizontal = false) {
    const maxValue = Math.max(...data.map(item => item.value));
    const chartHeight = 200;
    const barSpacing = 10;
    
    let chartHtml = '<div class="chart-bars' + (isHorizontal ? ' horizontal' : '') + '">';
    
    data.forEach(item => {
        const barSize = (item.value / maxValue) * (isHorizontal ? 250 : chartHeight);
        
        chartHtml += `
            <div class="chart-bar">
                <div class="chart-bar-label">${isHorizontal ? '' : item.month || item.source}</div>
                <div class="chart-bar-container">
                    <div class="chart-bar-value" style="${isHorizontal ? 
                        'width:' + barSize + 'px; background-color:' + color : 
                        'height:' + barSize + 'px; background-color:' + color}"></div>
                </div>
                ${isHorizontal ? '<div class="chart-bar-label">' + item.source + '</div>' : ''}
                <div class="chart-bar-value-label">${item.value}</div>
            </div>
        `;
    });
    
    chartHtml += '</div>';
    
    $(container).html(chartHtml);
}