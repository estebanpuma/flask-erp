function newModelForm(){
    return{

        //
        item: { code: '', color: '', line: '', subline: '', errors: ''},

        items: [],
        //compnentes para select inputs
        lines: [],
        sublines: [],
        colors: [],

        addItem() {
            this.items.push({
                serie: '', 
                serie_sizes:'',
                code: '', 
                detail: '',  
                qty: '', 
                unit: '', 
                errors: ''
            });
        },

        removeItem(index) {
            this.items.splice(index, 1); // Elimina el material por índice
        },


        async uploadFile() {
            const fileInput = this.$refs.fileInput.files[0];

            if (!fileInput) {
                alert("Por favor, selecciona un archivo antes de subirlo.");
                return;
            }

            const formData = new FormData();
            formData.append("file", fileInput);
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            try {
                const response = await fetch("/api/v1/bomfile/upload", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken // Incluye el token en los headers
                    },
                    body: formData
                });

                const result = await response.json();
                
                if (response.ok) {
                    let boomMaterials = result;
                    console.log(boomMaterials.boom)
                    console.log('vs ee', boomMaterials['boom']);
                    if (boomMaterials['boom']!=undefined && boomMaterials['boom'].length > 0) {
                
                        for(let i=0; i<boomMaterials.boom.length; i++){
                            let item = boomMaterials.boom[i];                  
                            let new_item = {
                                serie: item.serie_code,
                                serie_sizes:item.serie_sizes,
                                code: item.material_code,
                                detail:item.detail,
                                unit: item.unit,
                                qty: item.qty,
                                errors: item.errors
                            }
                            this.items.push(new_item);
                            console.log(';itempuhcado')
                            
                                
                        }
                            
                    }
                } else {
                    console.error("Errores en el archivo:", result.errors || result.error);
                }
            } catch (error) {
                console.error("Error en la solicitud:", error);
            }
        },

        
        async searchSerie(query,index){
            if(query.length>0){
                
                query = 'code='+query;
                
                console.log('Esta es la query'+query)

                try {
                    const response = await fetch(`/api/v1/sizeSeries?q=${query}`);
                    if (response.ok) {
                        let serie = await response.json();                      
                        
                        if (serie.name == null || serie.name == 0){
                            this.items[index]['serie_sizes'] = 'No existe'
                        }else{
                            this.items[index]['serie_sizes'] = serie.start_size +'-'+serie.end_size
                        }

                    } else {

                        console.error("Error al cargar las series");
                    }
                } catch (error) {
                    console.error("Hubo un problema con la solicitud:", error);
                }
            }
        },


        searchMaterial(query, index) {
            if (query.length > 0) {
                query = '<by_code>' + query
                console.log(query)
                fetch(`/api/v1/materials?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log(data)
                        console.log(data[0].name); 
                        console.log(data[0].unit); 
                        if (data[0].name==null){
                            this.items[index]['detail'] = 'Codigo no existe'
                            this.items[index]['errors'] = 'Codigo no existe'
                        }
                        else{
                            this.items[index]['detail'] = data[0].name
                            this.items[index]['unit'] = data[0].unit
                        }
                        
                        //console.log(this.items[index]['material'])
                    });
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

        async init(form_data, boomMaterials) {
            await this.fetchLines();
            await this.fetchSubLines();
            await this.fetchColors();

            

            if(form_data!=undefined){
                this.item.code = form_data.code
                this.item.line = form_data.line
                this.item.subline = form_data.subline
                this.item.color = form_data.color
                this.item.errors = form_data.errors
                console.log('errore sinside isi', this.item.errors)
            }
            if (boomMaterials!=undefined && boomMaterials.length > 0) {
                console.log(boomMaterials)
                for(let i=0; i<boomMaterials.length; i++){
                    let item = boomMaterials[i];                  
                    let new_item = {
                        serie: item.serie,
                        serie_sizes: item.serie_sizes,
                        code: item.code,
                        detail:item.detail,
                        unit: item.unit,
                        qty: item.qty,
                        
                    }
                    this.items.push(new_item);
                    console.log(';itempuhcado')
                    
                        
                }
                    
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

    }
}