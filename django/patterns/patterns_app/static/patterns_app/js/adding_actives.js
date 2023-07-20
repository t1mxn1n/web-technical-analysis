function makeActivesList(username) {
    let request = new XMLHttpRequest();
    let path = `http://127.0.0.1:8080/get_users_actives?username=${username}`
    request.open('GET', path, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            console.log(response);
            if (response['error_type'] === '-1') {
                let dropdown = document.getElementById("dropdown_actives");
                let fonds = response['fonds'];
                let crypto = response['crypto'];

                for(let i = 0; i < fonds.length; i++){
                    let opt = document.createElement("option");
                    opt.text = fonds[i] + " (акция)";
                    opt.value = fonds[i] + "_fonds";
                    opt.id = fonds[i];
                    dropdown.options.add(opt);
                }

                for(let i = 0; i < crypto.length; i++){
                    let opt = document.createElement("option");
                    opt.text = crypto[i] + " (криптовалюта)";
                    opt.value = crypto[i] + "_crypto";
                    opt.id = crypto[i];
                    dropdown.options.add(opt);
                }

                let user_actives_div = document.getElementById("user_actives_div");
                user_actives_div.appendChild(dropdown);

            }

        } else {
            console.log('error button')
        }
    }
    request.send()
}

function functionAddActiveToPool(type_active, active, username) {
    let warn = document.getElementById('warning_empty');
    let br = document.getElementById('br_');
    let warn_msg = document.getElementById("warning_msg");

    if (active === '') {
        warn.style.color = '#CC0000'
        warn.style.display = 'block';
        br.style.display = 'none';
        warn_msg.textContent = 'Для добавления введите название акции или криптовалюты';
        return
    }

    let request = new XMLHttpRequest();
    let path = `http://127.0.0.1:8080/add_user_active?type_active=${type_active}&active=${active}&username=${username}`
    request.open('GET', path, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            console.log(response);
            if (response['error_type'] === '0') {
                warn.style.color = '#CC0000'
                warn.style.display = 'block';
                br.style.display = 'none';
                warn_msg.textContent = `Не найден актив ${active}`
            }
            else if (response['error_type'] === '1') {
                warn.style.color = '#CC0000'
                warn.style.display = 'block';
                br.style.display = 'none';
                warn_msg.textContent = `Актив ${active.toUpperCase()} уже в вашем списке`
            }
            else if (response['error_type'] === '2') {
                warn.style.color = '#CC0000'
                warn.style.display = 'block';
                br.style.display = 'none';
                warn_msg.textContent = `Максимально допустимое количество активов для каждого рынка 5`
            }
            else {
                warn.style.color = '#008000'
                warn.style.display = 'block';
                br.style.display = 'none';

                let dropdown = document.getElementById("dropdown_actives");
                let opt = document.createElement("option");

                let active_upper = active.toUpperCase()
                if (type_active === 'fonds') {
                    opt.text = active_upper + " (акция)";
                    opt.value = active_upper + "_fonds";
                }
                else {
                    opt.text = active_upper + " (криптовалюта)";
                    opt.value = active_upper + "_crypto";
                }

                opt.id = active_upper;
                dropdown.options.add(opt);
                let user_actives_div = document.getElementById("user_actives_div");
                user_actives_div.appendChild(dropdown);

                warn_msg.textContent = `Актив ${active_upper} добавлен в ваш список`

            }
        } else {
            console.log('error button')
        }
    }
    request.send()

}

function removeActive(active, username) {
    let warn = document.getElementById('warning_empty_delete');
    let br = document.getElementById('br2_');
    let warn_msg = document.getElementById("warning_msg_delete");

    if (active === 'empty') {
        warn.style.color = '#CC0000'
        warn.style.display = 'block';
        br.style.display = 'none';
        warn_msg.textContent = 'Для удаления выберите актив из списка';
        return
    }
    else {
        warn.style.color = '#008000'
        warn.style.display = 'block';
        br.style.display = 'none';
        let active_value = active.split("_")[0];
        let active_type = active.split("_")[1];

        let request = new XMLHttpRequest();
        let path = `http://127.0.0.1:8080/delete_user_active?type_active=${active_type}&active=${active_value}&username=${username}`
        request.open('GET', path, true)
        request.onload = function () {
            if (request.status >= 200 && request.status < 400) {
                let response = JSON.parse(request.responseText);
                if (response['error_type'] === '0') {
                    warn_msg.textContent = `${active_value} не найден`;
                }
                else {
                    let option = document.querySelector(`option[value=${active}]`);
                    if (option) {
                        option.remove();
                    }
                    warn_msg.textContent = `${active_value} был удалён из вашего списка`;
                }
            } else {
                console.log('error button')
            }
        }
        request.send()
    }
}

function botAuth(username) {
    let login = document.getElementById('login_auth');
    let code = document.getElementById('code_auth');
    let code_label = document.getElementById('code_auth_label');
    let butt = document.getElementById('go_tg');

    let request = new XMLHttpRequest();
    let path = `http://127.0.0.1:8080/get_user_tg_code?username=${username}`;
    request.open('GET', path, true)
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            let response = JSON.parse(request.responseText);
            code_label.textContent = response['code'];
            login.style.display = 'block';
            code.style.display = 'block';
            butt.style.display = 'block';

        } else {
            console.log('error button')
        }
    }
    request.send()



}