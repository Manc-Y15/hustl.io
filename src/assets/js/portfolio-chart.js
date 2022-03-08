var assets_chart_elem = document.getElementById('assets_chart').getContext("2d");


const assets_data = {
    labels: ['$TSLA', '$BTC', '$AAPL', '$ZOOM', '$AMC'],
    datasets: [{
        label: 'Dataset 1',
        data: [15, 35, 30, 5, 15],
        backgroundColor: [
            "#1abc9c",
            "#2ecc71",
            "#27ae60",
            "#2980b9",
            "#8e44ad",
            "#f1c40f",
            "#e67e22",
            "#3498db",
            "#9b59b6",
            "#16a085",
            "#e74c3c",
            "#ecf0f1",
        ],
    }]
};

const assets_config = {
    type: 'pie',
    data: assets_data,
    options: {
        responsive: true,
        maintainAspectRatio: true,
        legend: {
            labels: {
                fontColor: 'white'
            }
        },
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Asset Distribution',
                color: "white"
            }
        },
    },
};



var assets_chart = new Chart(assets_chart_elem, assets_config);

var valuation_char_elem = document.getElementById('valuation_chart').getContext('2d');

var gradientStroke = valuation_char_elem.createLinearGradient(500, 0, 100, 0);
gradientStroke.addColorStop(0, 'rgba(26,188,156,1)');
gradientStroke.addColorStop(1, 'rgba(46,204,113,1)');

var gradientFill = valuation_char_elem.createLinearGradient(0, 0, 0, 500);
gradientFill.addColorStop(0.2, "rgba(26,188,156,0.3)");
gradientFill.addColorStop(1, "rgba(0, 0, 0, 0.0)");

var valuation_chart = new Chart(valuation_char_elem, {
    type: 'line',
    data: {
        labels: ["6 MON", "7 TUES", "8 WED", "9 THURS", "10 FRI", "11 SAT", "12 SUN"],
        datasets: [{
            label: "Data",
            borderColor: gradientStroke,
            pointBorderColor: gradientStroke,
            pointBackgroundColor: gradientStroke,
            pointHoverBackgroundColor: gradientStroke,
            pointHoverBorderColor: gradientStroke,
            pointBorderWidth: 10,
            pointHoverRadius: 10,
            pointHoverBorderWidth: 1,
            pointRadius: 3,
            fill: true,
            backgroundColor: gradientFill,
            borderWidth: 3,
            data: [50000, 51233, 53294, 54932, 55832, 58392, 60394]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: "#ecf0f1",
                    beginAtZero: false,
                    maxTicksLimit: 5,
                    padding: 20,
                    callback: function(value, index, values) {
                        return '$' + value;
                    }
                },
                gridLines: {
                    color: "#7f8c8d",
                    drawTicks: false,
                    display: false
                }

            }],
            xAxes: [{
                gridLines: {
                    zeroLineColor: "transparent",
                    color: "#7f8c8d3b"
                },
                ticks: {
                    padding: 20,
                    fontColor: "#ecf0f1",
                    fontStyle: "bold"
                }
            }]
        },
        animation: {
            easing: "easeInOutBack"
        }
    }
});