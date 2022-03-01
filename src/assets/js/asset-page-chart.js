function init_charts(overall_data) {
    var valuation_char_elem = document.getElementById('valuation_chart').getContext('2d');

    var gradientStroke = valuation_char_elem.createLinearGradient(500, 0, 100, 0);
    gradientStroke.addColorStop(0, 'rgba(26,188,156,1)');
    gradientStroke.addColorStop(1, 'rgba(46,204,113,1)');

    var gradientFill = valuation_char_elem.createLinearGradient(0, 0, 0, 500);
    gradientFill.addColorStop(0.2, "rgba(26,188,156,0.3)");
    gradientFill.addColorStop(1, "rgba(0, 0, 0, 0.0)");

    return new Chart(valuation_char_elem, {
        type: 'line',
        data: {
            labels: overall_data['dates'],
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
                data: overall_data['value_history'],
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
                            return '$' + value.toFixed(2);
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
            },
            layout: {
                padding: {
                    top: 10
                }
            }
        }
    });

}