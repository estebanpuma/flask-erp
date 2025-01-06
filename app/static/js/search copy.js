document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('docsearch-input');
    const searchList = document.getElementById('docsearch-list');



    searchInput.addEventListener('input', function() {
        let query = searchInput.value;

        if (query.length > 0) {
            fetch(`/api/v1/search/client?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchList.innerHTML = '';
                    console.log(data)
                    data.forEach((item, index) => {
                        const li = document.createElement('li');
                        li.setAttribute('id', `docsearch-item-${index}`);
                        li.className = "list-group-item d-flex justify-content-between align-items-start btn";
                        li.dataset.id = item.id;
                        const cardContainer = document.createElement("div");
                        cardContainer.className = "ms-2 me-auto";
                        const divCode = document.createElement("div");
                        divCode.className = "fw-medium fs-6";
                        divCode.textContent = item.ruc_or_ci;
                        const div1 = document.createElement("div");
                        div1.className = "fw-bold";
                        div1.textContent = item.name;
                        const div2 = document.createElement("div");
                        div2.textContent =  "Ciudad";
                        const i = document.createElement("i")
                        i.className = "bi bi-chevron-right"

                        cardContainer.appendChild(divCode)
                        cardContainer.appendChild(div1);
                        cardContainer.appendChild(div2);
                        
                        li.appendChild(cardContainer);
                        li.appendChild(i)

                        li.addEventListener("click", function() {
                            get_data(item);  // Llamar a get_data con el ID seleccionado
                        });

                        searchList.appendChild(li);
                    });
                    searchList.style.display = 'block';
                });

        } else {
            searchList.innerHTML = '';
        }
    });

    function get_data(data){
        console.log('lee click')
        
        console.log(data)
        // solicitud AJAX para obtener los detalles del resultado seleccionado
        
                // Llena el formulario con los datos del resultado seleccionado
        document.getElementById('client_type').value = data.client_type || '';
        document.getElementById('name').value = data.name || '';
        document.getElementById('ruc_or_ci').value = data.ruc_or_ci || '';
        document.getElementById('email').value = data.email || '';
        document.getElementById('city').value = data.city || '';
        document.getElementById('address').value = data.address || '';
        document.getElementById('phone').value = data.phone || '';
        //document.getElementById('category').value = data.category || '';
            
        searchList.style.display = 'none';
        }

        document.addEventListener('click', function(event) {
            if (!searchList.contains(event.target) && event.target !== searchInput) {
                searchList.style.display = 'none';
            }
        });
        
});