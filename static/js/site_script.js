const site_id = window.location.pathname.split('/').pop();

function load_site() {
    fetch(`/api/sites/${site_id}`)
        .then(response => response.json())
        .then(template_project => {
            document.getElementById('site-container').innerHTML = `
                    <div class="site_text">
                        <h2>${template_project.about}</h2>
                        <h2>${template_project.explanation}</h2>
                        <h2>Вы можете просмотреть базовый шаблон такого сайта, относительно которого будет<br>
                        создаваться уже готовый и полностью функциональный сайт.</h2>
                    </div>
                    <p class="explanation">*Ниже вы можете запустить пробный шаблон такого сайта.</p>

                    <button class="site_button" onclick="window.location.href='/site/runsite/${template_project.id}'">
                        Открыть Сайт
                    </button>
                    <button class="site_button" onclick="window.location.href='/site/closesite/${template_project.id}'">
                        Закрыть Сайт
                    </button>

                    <p class="explanation">*При запуске сайт автоматически закроется через 10 минут,<br>
                    но вы можете предварительно завершить его работу.</p>

                    <button class="site_button" onclick="window.location.href='/site/buysite/${template_project.id}'">
                        Купить Сайт
                    </button>
                    `;
        })
}
function nouser_load_site() {
    fetch(`/api/sites/${site_id}`)
        .then(response => response.json())
        .then(template_project => {
            document.getElementById('site-container').innerHTML = `
                    <div class="site_text">
                        <h2>${template_project.about}</h2>
                        <h2>${template_project.explanation}</h2>
                        <h2>Вы можете просмотреть базовый шаблон такого сайта, относительно которого будет<br>
                        создаваться уже готовый и полностью функциональный сайт.</h2>
                    </div>
                    <h3>Для запуска сайта, вам необходимо авторизоваться.</h3>
                    <p class="explanation">*Ниже вы можете запустить пробный шаблон такого сайта.</p>
            
                    <button class="disabled_site_button" disabled="disabled">
                        Открыть Сайт
                    </button>
                    <button class="disabled_site_button" disabled="disabled">
                        Закрыть Сайт
                    </button>
            
                    <p class="explanation">*При запуске сайт автоматически закроется через 10 минут,<br>
                        но вы можете предварительно завершить его работу.
                    </p>
            
                    <button class="disabled_site_button" disabled="disabled">
                        Купить Сайт
                    </button>
                    `;
        })
}

async function checkAuth() {
    try {
        const response = await fetch('/check-user');
        const data = await response.json();

        if (data.authenticated) {
            return true;
        } else {
            return false;
        }
    } catch (error) {
        return false;
    }
}


checkAuth().then(isAuthenticated => {
    if (isAuthenticated) {
        load_site()
    } else {
        nouser_load_site()
    }
});



