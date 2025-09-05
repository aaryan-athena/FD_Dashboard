// Dashboard JavaScript
let timelineChart, severityChart, locationChart;
let currentPage = 1;
let totalPages = 1;

// Initialize charts
function initializeCharts(stats) {
    createTimelineChart(stats.timeline);
    createSeverityChart(stats.by_severity);
    createLocationChart(stats.by_location);
}

// Timeline Chart
function createTimelineChart(timelineData) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    // Prepare data for last 30 days
    const last30Days = [];
    const counts = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        last30Days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        counts.push(timelineData[dateStr] || 0);
    }
    
    if (timelineChart) {
        timelineChart.destroy();
    }
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: last30Days,
            datasets: [{
                label: 'Falls Detected',
                data: counts,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
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
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#007bff',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                point: {
                    hoverRadius: 8
                }
            }
        }
    });
}

// Severity Chart
function createSeverityChart(severityData) {
    const ctx = document.getElementById('severityChart').getContext('2d');
    
    if (severityChart) {
        severityChart.destroy();
    }
    
    severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High'],
            datasets: [{
                data: [
                    severityData.Low || 0,
                    severityData.Medium || 0,
                    severityData.High || 0
                ],
                backgroundColor: [
                    '#28a745',
                    '#ffc107',
                    '#dc3545'
                ],
                borderWidth: 0,
                hoverBorderWidth: 3,
                hoverBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            cutout: '60%'
        }
    });
}

// Location Chart
function createLocationChart(locationData) {
    const ctx = document.getElementById('locationChart').getContext('2d');
    
    const locations = Object.keys(locationData);
    const counts = Object.values(locationData);
    
    if (locationChart) {
        locationChart.destroy();
    }
    
    locationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: locations,
            datasets: [{
                label: 'Falls',
                data: counts,
                backgroundColor: 'rgba(0, 123, 255, 0.8)',
                borderColor: '#007bff',
                borderWidth: 1,
                borderRadius: 5
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
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Refresh data
async function refreshData() {
    showLoading();
    
    try {
        const [statsResponse, fallsResponse] = await Promise.all([
            fetch('/api/stats'),
            fetch(`/api/falls?page=${currentPage}&per_page=10`)
        ]);
        
        const stats = await statsResponse.json();
        const fallsData = await fallsResponse.json();
        
        // Update stats cards
        updateStatsCards(stats);
        
        // Update charts
        initializeCharts(stats);
        
        // Update table
        updateFallsTable(fallsData.falls);
        
        // Update pagination
        updatePagination(fallsData);
        
        updateLastUpdated();
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        showError('Failed to refresh data');
    } finally {
        hideLoading();
    }
}

// Update stats cards
function updateStatsCards(stats) {
    const cards = document.querySelectorAll('.stat-card h4');
    if (cards.length >= 4) {
        cards[0].textContent = stats.today;
        cards[1].textContent = stats.this_week;
        cards[2].textContent = stats.this_month;
        cards[3].textContent = stats.total;
    }
}

// Update falls table
function updateFallsTable(falls) {
    const tbody = document.querySelector('#fallsTable tbody');
    tbody.innerHTML = '';
    
    falls.forEach(fall => {
        const row = createFallRow(fall);
        tbody.appendChild(row);
    });
}

// Create fall table row
function createFallRow(fall) {
    const row = document.createElement('tr');
    
    const severityClass = `severity-${fall.severity.toLowerCase()}`;
    const formattedTime = formatDateTime(fall.timestamp);
    
    row.innerHTML = `
        <td>
            <div class="timestamp">${formattedTime}</div>
        </td>
        <td>
            <span class="badge bg-secondary">
                <i class="fas fa-location-dot me-1"></i>
                ${fall.location}
            </span>
        </td>
        <td>
            <span class="badge bg-secondary">
                <i class="fas fa-microchip me-1"></i>
                ${fall.person_id}
            </span>
        </td>
        <td>
            <span class="badge bg-info">
                <i class="fas fa-brain me-1"></i>
                ${fall.detection_method || 'Motion'}
            </span>
        </td>
        <td>
            <span class="badge ${severityClass}">
                ${fall.confidence}
            </span>
        </td>
        <td>${fall.duration}s</td>
        <td>
            <button class="btn btn-sm btn-outline-primary me-1" 
                    onclick="viewFallDetail('${fall.id}')">
                <i class="fas fa-eye"></i>
                View
            </button>
            <button class="btn btn-sm btn-outline-success" 
                    onclick="playVideo('${fall.video_url}', '${fall.id}')">
                <i class="fas fa-play"></i>
                Video
            </button>
        </td>
    `;
    
    return row;
}

// Format datetime
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// View fall detail
function viewFallDetail(fallId) {
    window.open(`/fall/${fallId}`, '_blank');
}

// Play video
async function playVideo(videoUrl, fallId) {
    try {
        showLoading();
        
        // Check if it's already a full URL (like Cloudinary)
        if (videoUrl.startsWith('http://') || videoUrl.startsWith('https://')) {
            // Use the URL directly
            const video = document.getElementById('fallVideo');
            video.src = videoUrl;
            
            const videoInfo = document.getElementById('videoInfo');
            videoInfo.textContent = `Fall ID: ${fallId} | Video: Direct URL`;
            
            const modal = new bootstrap.Modal(document.getElementById('videoModal'));
            modal.show();
        } else {
            // Get signed URL for Firebase Storage videos
            const response = await fetch(`/api/video/${videoUrl}`);
            const data = await response.json();
            
            if (data.url) {
                const video = document.getElementById('fallVideo');
                video.src = data.url;
                
                const videoInfo = document.getElementById('videoInfo');
                videoInfo.textContent = `Fall ID: ${fallId} | Video: ${videoUrl}`;
                
                const modal = new bootstrap.Modal(document.getElementById('videoModal'));
                modal.show();
            } else {
                showError('Video not available');
            }
        }
    } catch (error) {
        console.error('Error loading video:', error);
        showError('Failed to load video');
    } finally {
        hideLoading();
    }
}

// Update pagination
function updatePagination(data) {
    totalPages = Math.ceil(data.total / data.per_page);
    currentPage = data.page;
    
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    // Previous button
    const prevItem = document.createElement('li');
    prevItem.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevItem.innerHTML = `
        <a class="page-link" href="#" onclick="loadPage(${currentPage - 1})">
            <i class="fas fa-chevron-left"></i>
        </a>
    `;
    pagination.appendChild(prevItem);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${i === currentPage ? 'active' : ''}`;
        pageItem.innerHTML = `
            <a class="page-link" href="#" onclick="loadPage(${i})">${i}</a>
        `;
        pagination.appendChild(pageItem);
    }
    
    // Next button
    const nextItem = document.createElement('li');
    nextItem.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextItem.innerHTML = `
        <a class="page-link" href="#" onclick="loadPage(${currentPage + 1})">
            <i class="fas fa-chevron-right"></i>
        </a>
    `;
    pagination.appendChild(nextItem);
    
    // Update records info
    const recordsInfo = document.getElementById('recordsInfo');
    const totalRecords = document.getElementById('totalRecords');
    const startRecord = (currentPage - 1) * data.per_page + 1;
    const endRecord = Math.min(currentPage * data.per_page, data.total);
    
    recordsInfo.textContent = `${startRecord}-${endRecord}`;
    totalRecords.textContent = data.total;
}

// Load page
async function loadPage(page) {
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    showLoading();
    
    try {
        const response = await fetch(`/api/falls?page=${page}&per_page=10`);
        const data = await response.json();
        
        updateFallsTable(data.falls);
        updatePagination(data);
        
    } catch (error) {
        console.error('Error loading page:', error);
        showError('Failed to load page');
    } finally {
        hideLoading();
    }
}

// Update last updated time
function updateLastUpdated() {
    const lastUpdated = document.getElementById('lastUpdated');
    lastUpdated.textContent = new Date().toLocaleTimeString();
}

// Show loading spinner
function showLoading() {
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('d-none');
}

// Hide loading spinner
function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.add('d-none');
}

// Show error message
function showError(message) {
    // Create a toast or alert for error messages
    console.error(message);
    
    // You can implement a toast notification here
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Handle video modal events
document.getElementById('videoModal').addEventListener('hidden.bs.modal', function () {
    const video = document.getElementById('fallVideo');
    video.pause();
    video.src = '';
});

// Handle escape key for modals
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const video = document.getElementById('fallVideo');
        if (video && !video.paused) {
            video.pause();
        }
    }
});

// Auto-refresh functionality
let autoRefreshInterval;

function startAutoRefresh(intervalMs = 30000) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        refreshData();
    }, intervalMs);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Start auto-refresh when page loads
document.addEventListener('DOMContentLoaded', function() {
    startAutoRefresh();
});

// Stop auto-refresh when page is hidden
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});
