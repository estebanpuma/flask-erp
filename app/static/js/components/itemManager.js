
function itemManager() {
    return {
        items: [],

        addMaterial() {
            this.items.push({
                size: '', 
                code: '', 
                group: '', 
                name: '', 
                qty: '', 
                unit: '', 
                errors: ''
            });
        },

        removeMaterial(index) {
            this.items.splice(index, 1);
        },

        validateMaterials() {
            let isValid = true;
            this.items.forEach((item) => {
                item.errors = '';
                if (!item.code) {
                    item.errors = 'El código del material es obligatorio.';
                    isValid = false;
                }
                if (!item.qty || item.qty <= 0) {
                    item.errors = 'La cantidad debe ser mayor que cero.';
                    isValid = false;
                }
            });
            return isValid;
        }
    };
}
