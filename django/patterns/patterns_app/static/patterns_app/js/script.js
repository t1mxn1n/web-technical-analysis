function removeOptions(selectElement) {
   var i, L = selectElement.options.length - 1;
   for(i = L; i >= 0; i--) {
      selectElement.remove(i);
   }
}

function getUsersActives(username, type_active, check_list) {
    let request = new XMLHttpRequest();
    request.open('GET', `http://127.0.0.1:8080/get_users_actives?username=${username}`, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            let actives = response['actives'];
            let dropdown = document.getElementById("dropdown_2");

            actives = response[type_active];

            for(let i = 0; i < actives.length; i++){
                if (check_list.includes(actives[i])) continue;
                let opt = document.createElement("option");
                opt.text = actives[i] + " (Добавлен вами)";
                opt.value = actives[i] + `_${type_active}`;
                opt.id = actives[i];
                dropdown.options.add(opt);
            }
            //
            let div_d2 = document.getElementById("stage1");
            div_d2.appendChild(dropdown);

        } else {
            console.log('error dropdown')
        }
    }
    request.send()

}

function showInputField(username) {
    let dropdown_1 = document.getElementById("dropdown_1");
    let dropdown_2 = document.getElementById("dropdown_2");
    let dropdown_3 = document.getElementById("dropdown_3");
    let button = document.getElementById("res_button");
    let stage1 = document.getElementById("stage1");
    let stage2 = document.getElementById("stage2");
    let graphic = document.getElementById("img_div");
    let indicators = document.getElementById("indicators_div");
    let patterns = document.getElementById("patterns_div");
    let choose_active = false;
    let choose_resolution = false;
    let show_button = false;
    let type_active = 'empty', active = 'empty2', resolution = 'empty3';
    let first_time = true;

    if (dropdown_1.value === "empty") {
        stage1.style.display = "none";
        stage2.style.display = "none";
        graphic.style.display = "none";
        button.style.display = "none";
        indicators.style.display = "none";
        choose_active = false;
        choose_resolution = false;
        let imgElement = document.getElementById("img");
        imgElement.src = "";
        active = 'empty2';
        resolution = 'empty3';
        dropdown_2.value = 'empty2';
        dropdown_3.value = 'empty3';
        removeOptions(document.getElementById('dropdown_2'));

    }

    if (dropdown_1.value === "fonds" || dropdown_1.value === "crypto") {

        if ((dropdown_1.value === "fonds") && (document.getElementById("crypto") != null)) {

            removeOptions(document.getElementById('dropdown_2'));
        }

        if ((dropdown_1.value === "crypto") && (document.getElementById("fonds") != null)) {
            removeOptions(document.getElementById('dropdown_2'));
        }

        if (document.getElementById(dropdown_1.value) == null) {
            let request = new XMLHttpRequest();
            request.open('GET', `http://127.0.0.1:8080/get_actives?type_active=${dropdown_1.value}`, true)
            request.onload = function () {
                if (request.status >= 200 && request.status < 400) {
                    let response = JSON.parse(request.responseText);
                    let actives = response['actives'];
                    let dropdown = document.getElementById("dropdown_2");
                    //dropdown.onchange = showInputField();

                    let opt = document.createElement("option");
                    opt.text = 'Выбрать актив...';
                    opt.value = 'empty2';
                    dropdown.options.add(opt);
                    let values_list = [];
                    for(let i = 0; i < actives.length; i++){
                        let opt = document.createElement("option");
                        opt.text = actives[i];
                        opt.value = actives[i];
                        values_list.push(opt.value);
                        opt.id = dropdown_1.value;
                        dropdown.options.add(opt);
                    }

                    getUsersActives(username, dropdown_1.value, values_list);

                    let div_d2 = document.getElementById("stage1");
                    div_d2.appendChild(dropdown);


                } else {
                    console.log('error dropdown')
                }
            }
            request.send()


            stage1.style.display = "block";
            choose_active = true;
            type_active = dropdown_1.value;

        }

    }

    if (dropdown_2.value != '') {
        stage2.style.display = "block";
        choose_resolution = true;
        active = dropdown_2.value;
    }


    if (dropdown_3.value != 'empty3') {
        resolution = dropdown_3.value;
    }

    if ((dropdown_1.value === "fonds" || dropdown_1.value === "crypto") && (dropdown_2.value != '' && dropdown_2.value != 'empty2') && (dropdown_3.value != 'empty3')) {
        button.style.display = "block";
        indicators.style.display = "flex";
        patterns.style.display = "flex";
        // console.log(type_active, active, resolution)
    }
    else {
        button.style.display = "none";
        indicators.style.display = "none";
        patterns.style.display = "none";
        let imgElement = document.getElementById("img");
        let imgElementDiv = document.getElementById("img_div");
        imgElementDiv.style.display = 'none';
        imgElement.src = "";
    }
}

function functionToExecute(type, active, resolution) {
    let indicators = ['#ma', '#rsi', '#bb', '#tp', '#has', '#talib'];
    let indicators_code = '';
    for (let i = 0; i < indicators.length; i++) indicators_code += Number(document.querySelector(indicators[i]).checked).toString();

    let request = new XMLHttpRequest();
    let path = `http://127.0.0.1:8080/get_plot?type_active=${type}&active=${active}&resolution=${resolution}&ind_code=${indicators_code}`;
    request.open('GET', path, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            let imgElement = document.getElementById("img");
            let path = '/static/' + response['name'];
            imgElement.src = path;
            let imgDiv = document.getElementById("img_div");
            imgDiv.style.display = "block";

        } else {
            console.log('error button')
        }
    }
    request.send()
}

function getStringIndicators(indicators) {
    let res = [];
    for (let i = 0; i < indicators.length; i++){
        if (indicators[i] === 'ma') res.push('MA(средняя скользящая)');
        if (indicators[i] === 'rsi') res.push('RSI(индекс относительной силы)');
        if (indicators[i] === 'bollinger') res.push('Линии Боллинджера');
        if (indicators[i] === 'triangle') res.push('Фигура треугольник');
        if (indicators[i] === 'talib') res.push('Свечные индикаторы');
    }
    return res;
}

function makeList(signal, type_active) {
    let div1 = document.createElement('div');
    div1.id = 'div1';
    div1.className = 'd-flex text-body-secondary pt-3';
    let div2 = document.createElement('div');
    div2.id = 'div2';
    div2.className = 'pb-3 mb-0 small lh-sm border-bottom w-100';
    let div3 = document.createElement('div');
    div3.id = 'div3';
    div3.className = "d-flex justify-content-between";

    let strong = document.createElement('strong');
    strong.textContent = `${signal['active']} (${signal['interval']})`;  // tut
    strong.className = 'text-gray-dark';

    let span = document.createElement('span');
    span.className = 'd-block';

    let indicators = getStringIndicators(signal['indicator']);
    span.textContent = indicators; // tut

    let img = document.createElement('img');
    img.className = 'bd-placeholder-img flex-shrink-0 me-2 rounded';
    img.width = 32;
    img.height = 32;
    img.src = "/static/trend_up.png";

    div1.appendChild(img);
    div3.appendChild(strong);
    // div3.appendChild(a);
    div2.appendChild(div3);
    div2.appendChild(span);
    div1.appendChild(div2);


    document.getElementById(`signals_${type_active}`).appendChild(div1);
}

function makeListByActive(type_active) {

    let request = new XMLHttpRequest();
    let path = `http://127.0.0.1:8080/get_public_signals?type_active=${type_active}`;
    request.open('GET', path, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            let signals = response['signals'][0]['signals'];
            for (let i = 0; i < signals.length; i++){
                makeList(signals[i], type_active);
            }

            let small = document.createElement('small');
            small.className = 'd-block text-end mt-3';
            let a = document.createElement('a');
            a.href = 'http://127.0.0.1:8000/ta/';
            a.textContent = 'Перейти на страницу технического анализа';
            small.appendChild(a);
            document.getElementById(`signals_${type_active}`).appendChild(small);

        } else {
            console.log('error button')
        }
    }
    request.send()
}

function makeSignalsList(aboba) {
    makeListByActive('crypto');
    makeListByActive('fonds');
}

