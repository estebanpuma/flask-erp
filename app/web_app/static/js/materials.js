
function materialsTable() {
    console.log("JS externo materials.js cargado correctamente");
    return {
        
        materials: [],
        loading: false,
        error: null,



        fetchMaterials() {
            this.loading = true;
            console.log('iniit fecth')
            fetch('/api/v1/materials')
                .then(res => {
                    if (!res.ok) throw new Error("Error al obtener materiales");
                    return res.json();
                })
                .then(data => {
                    this.materials = data || [];
                    console.log(data)
                })
                .catch(err => {
                    this.error = err.message;
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        openCreateModal() {
            alert("Abrir modal de creación (a implementar)");
        }
    }
}
