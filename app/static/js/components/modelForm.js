
function itemManager() {
    return {
        items: [],

        addMaterial() {
            this.items.push({
                serie: '', 
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



function newModelForm() {
    return {
        // Datos del modelo (incluyendo boom como parte del objeto item)
        item: { code: '', color: '', line: '', subline: '', errors: '', boom: [] },
        lines: [],
        sublines: [],
        colors: [],
        series: [],

        addSerie() {
            this.fetchSizeSeries()
            this.item.boom.push({
                serie: '',
                materials: [],
                errors: ''
            });
        },

        addMaterial(index) {
            console.log('inside  addMAteril', index)
            const serie = this.item.boom[index];

            serie.materials.push({ 
                code: '', 
                group: '', 
                name: '', 
                qty: '', 
                unit: '', 
                errors: ''
            });
            console.log('pass serie', serie)
        },

        removeMaterial(index) {
            this.items.splice(index, 1);
        },

        // Función para eliminar una serie específica de boom
        removeSerie(index) {
            this.item.boom.splice(index, 1);
        },
    

        // Función para eliminar un material de una serie específica en boom
        removeMaterial(serieIndex, materialIndex) {
            this.item.boom[serieIndex].boomMaterials.splice(materialIndex, 1);
        },
    
        searchMaterial(query, index, mindex) {
            if (query.length > 0) {
                query = '<by_code>' + query
                console.log(query)
                fetch(`/api/v1/materials?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                     
                        if (data[0].name==null){
                            this.item.boom[index].materials[mindex].name = 'Codigo no existe'
                        }
                        else{
                            this.item.boom[index].materials[mindex].name = data[0].name
                            this.item.boom[index].materials[mindex].unit = data[0].unit
                        }
                        
                        //console.log(this.items[index]['material'])
                    });
            }
        },

        setSizeSerie(i, serie_id){
            
            console.log('holi soy serie id', serie_id, typeof(serie_id))
            
            if(serie_id !== undefined && serie_id !== null && serie_id !== ''){
                let serie_name = this.fetchSizeSerie(serie_id)
                return serie_name
            }else{
                return 'Serie'
            }
            
        },

        async fetchSizeSerie(serie_id) {
            try {
                console.log(serie_id, typeof(serie_id))
                let serie = parseInt(serie_id)
                console.log(serie, typeof(serie))
                const response = await fetch(`/api/v1/sizeSeries/${serie}`);
                if (response.ok) {
                    serie = await response.json();
                    console.log('serie', serie.name)
                    return serie.name
                } else {
                    console.error("Error al cargar la serie");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
        },
        
        async fetchSizeSeries() {
            try {
                const response = await fetch('/api/v1/sizeSeries');
                if (response.ok) {
                    this.series = await response.json();
                    console.log('carga sizeSeries')
                } else {
                    console.error("Error al cargar las series");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
        },
        
        async fetchLines() {
            try {
                const response = await fetch('/api/v1/lines');
                if (response.ok) {
                    this.lines = await response.json();
                    console.log('carga lineas')
                } else {
                    console.error("Error al cargar las lineas");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
        },

        async fetchSubLines() {
            try {
                const response = await fetch('/api/v1/sublines');
                if (response.ok) {
                    this.sublines = await response.json();
                } else {
                    console.error("Error al cargar las sublineas");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
        },

        async fetchColors() {
            try {
                const response = await fetch('/api/v1/colors');
                if (response.ok) {
                    this.colors = await response.json();
                } else {
                    console.error("Error al cargar colores");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
        },

        async init(form_data) {
            await this.fetchLines();
            await this.fetchSubLines();
            await this.fetchColors();

            if(form_data!=undefined){
                this.item.code = form_data.code
                this.item.line = form_data.line
                this.item.subline = form_data.subline
                this.item.color = form_data.color
                this.item.errors = form_data.errors
            }
            
        },

        async fetchLineCode() {
            try {
                const response = await fetch(`/api/v1/lines/${this.item.line}`);
                if (response.ok) {
                    const line = await response.json();
                    return line.code;
                } else {
                    console.error("Error al cargar la línea");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
            return '';
        },

        async fetchSubLineCode() {
            try {
                const response = await fetch(`/api/v1/sublines/${this.item.subline}`);
                if (response.ok) {
                    const subline = await response.json();
                    return subline.code;
                } else {
                    console.error("Error al cargar la sublínea");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
            return '';
        },

        async fetchColorCode() {
            try {
                const response = await fetch(`/api/v1/colors/${this.item.color}`);
                if (response.ok) {
                    const color = await response.json();
                    return color.code;
                } else {
                    console.error("Error al cargar codigo de color");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
            return '';
        },

        async fetchNextModelCode(subCode) {
            try {
                const response = await fetch(`/api/v1/next_code_model/${subCode}`);
                if (response.ok) {
                    const nextCode = await response.json();
                    return nextCode;
                } else {
                    console.error("Error al cargar el codigo");
                }
            } catch (error) {
                console.error("Hubo un problema con la solicitud:", error);
            }
            return '';
        },

        



        async updateCode() {
            let lineCode = '';
            let sublineCode = '';
            let colorCode = '';
            if (this.item.line){
                lineCode = await this.fetchLineCode();
            }
            if(this.item.subline){
                sublineCode = await this.fetchSubLineCode();
            }
            if (this.item.color ){
                colorCode = await this.fetchColorCode()
            }
            
            let subCode = lineCode + sublineCode;
            if(lineCode){
                next_code = await this.fetchNextModelCode(subCode)
                this.item.code = next_code.next_code + colorCode;
            }else{
                this.item.code = '';
            }
        }
    };
}
