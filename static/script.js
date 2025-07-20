document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        
        // Get form data
        const formData = new FormData(form);
        
        // Make request
        fetch('/scrape-data', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            
            if (data.status === 'success') {
                displayResults(data.data, data.charts);
                results.classList.remove('hidden');
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            loading.classList.add('hidden');
            alert('Error: ' + error.message);
        });
    });
});

function displayResults(data, charts) {
    // Update stats
    document.getElementById('totalFlights').textContent = data.total_flights;
    document.getElementById('avgPrice').textContent = 'AUD $' + data.average_price;
    document.getElementById('priceRange').textContent = `$${data.price_range.min} - $${data.price_range.max}`;
    document.getElementById('avgOccupancy').textContent = data.demand_analysis.average_occupancy + '%';
    
    // Display charts
    if (charts.price_trend) {
        Plotly.newPlot('priceChart', JSON.parse(charts.price_trend).data, JSON.parse(charts.price_trend).layout);
    }
    
    if (charts.airline_popularity) {
        Plotly.newPlot('airlineChart', JSON.parse(charts.airline_popularity).data, JSON.parse(charts.airline_popularity).layout);
    }
    
    // Display recommendations
    const recommendationsList = document.getElementById('recommendations');
    recommendationsList.innerHTML = '';
    
    data.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recommendationsList.appendChild(li);
    });
}