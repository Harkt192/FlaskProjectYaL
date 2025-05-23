fetch('/api/sites')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('sites-container');
                data.template_projects.forEach(template_project => {
                    container.innerHTML += `
                        <div>
                            <a class="widget-link" href="/sites/${template_project.id}">
                                <div class="widget" >
                                    <h1>${template_project.site_name}</h1>
                                    <h3>${template_project.about}</h3>
                                    <h3>${template_project.explanation}</h3>
                                </div>
                            </a>
                        </div>
                    `;
                });
            });