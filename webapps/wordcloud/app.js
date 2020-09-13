let allRows;
let webAppConfig = dataiku.getWebAppConfig()['webAppConfig'];
let webAppDesc = dataiku.getWebAppDesc()['chart']

window.parent.postMessage("sendConfig", "*");

function set_simple_svg(params){
    let headers = new Headers();
    let init = {
        method : 'GET',
        headers : headers
    };
    let url = getWebAppBackendUrl('/get_svg')+'/'+JSON.stringify(params);

    fetch(url, init)
    .then(function(response){
        response.json()
        .then(function(data){
            for (var chart of data) {
                
                var row = document.createElement('div');
                row.setAttribute('class', 'row')

                var col = document.createElement('div');
                col.setAttribute('class', 'col')
                row.appendChild(col)
                
                var worcloud = document.createElement('div');
                worcloud.innerHTML = chart.svg;
                worcloud.setAttribute('class', 'single-chart');
                col.appendChild(worcloud);

                document.getElementById('wordcloud').appendChild(row);
            }
        })
    })
}

function set_subcharts_svg(params){
    let headers = new Headers();
    let init = {
        method : 'GET',
        headers : headers
    };
    let url = getWebAppBackendUrl('/get_svg')+'/'+JSON.stringify(params);

    fetch(url, init)
    .then(function(response){
        response.json()
        .then(function(data){
            for (var chart of data) {
                
                var row = document.createElement('div');
                row.setAttribute('class', 'row subcharts')

                var title = document.createElement('div');
                title.innerHTML = chart.subchart;
                title.setAttribute('class', 'col-md-2 align-self-center');
                row.appendChild(title);
                
                var worcloud = document.createElement('div');
                worcloud.innerHTML = chart.svg;
                worcloud.setAttribute('class', 'col-md-10 py-4');
                row.appendChild(worcloud);

                document.getElementById('wordcloud').appendChild(row);
            }
        })
    })
}

window.addEventListener('message', function(event) {
    if (event.data) {

        event_data = JSON.parse(event.data);

        // Load webapp config
        webAppConfig = event_data['webAppConfig'];

        var params = {
            dataset_name: webAppConfig['dataset'],
            text_column: webAppConfig['text_column'],
            language: webAppConfig['language'],
            subchart_column: webAppConfig['subchart_column'],
            lemmatize: webAppConfig['lemmatize'],
            tokens_filter: webAppConfig['tokens_filter']
        }

        console.log(webAppConfig);

        // Check webapp config
        try {
            checkWebAppParameters(webAppConfig, webAppDesc);
        } catch (e) {
            dataiku.webappMessages.displayFatalError(e.message);
            return;
        }

        // Clear previous webapp HTML
        var div = document.getElementById('wordcloud');
        while(div.firstChild){
            div.removeChild(div.firstChild);
        };
		
		/*
		// Add loader
		div.setAttribute('class', 'dku-loader');
        */

        // Load new webapp HTML
        if (params.subchart_column) {
            set_subcharts_svg(params);
        } else {
            set_simple_svg(params);
        }


        
    } 
 });