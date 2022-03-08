

function init_assets_chart(overall_data) {

    var assets_chart_elem = document.getElementById('assets_chart').getContext("2d");

    converted_cols = [];

    for (col of overall_data['colours']) {
        converted_cols.push(
                String(getComputedStyle(
                    document.getElementById('assets_chart')
                ).getPropertyValue(col)).trim()
        );
    }

    const assets_data = {
        labels: overall_data['tickets'],
        datasets: [{
            label: 'Dataset 1',
            data: overall_data['data'],
            backgroundColor: converted_cols,
            borderColor: "#bdc3c7"
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



    return new Chart(assets_chart_elem, assets_config);

}
