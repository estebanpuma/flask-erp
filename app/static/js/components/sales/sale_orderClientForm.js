function sale_orderClientForm() {
    return {
        query: '',
        results: [],
        client: {},
        clientErrors:{},
        modal: false,

        // Función para buscar clientes
        search() {
            if (this.query.length > 0) {
                fetch(`/api/v1/search/client?q=${this.query}`)
                    .then(response => response.json())
                    .then(data => {
                        this.results = data;
                    })
                    .catch(error => console.error('Error al buscar clientes:', error));
            } else {
                this.results = [];
            }
        },

        // Función para seleccionar un cliente
        selectClient(item) {
            this.client = item;
            console.log(this.client)
            this.results = []; // Ocultar resultados después de seleccionar
        }
    };
}