function materialForm() {
    return {
        items: [], // Inicializa un array vacio para almecenar todos los items
        //{ code: '', material: '', unit: '', qty: 0, errors: '' }
        init(itemsFromForm, errors) {
            // Rellenar items desde el formulario si ya hay datos
            
            console.log('Ejecutando init por primera vez');
            console.log('contador de init')
            console.log(itemsFromForm)
            console.log('errors',errors)  
            
            if (itemsFromForm!=undefined && itemsFromForm.length > 0) {
                
                for(let i=0; i<itemsFromForm.length; i++){
                    let item = itemsFromForm[i];
                    let error = errors && errors[i] ? errors[i] : {};
                    
                    let new_item = {
                        code: item.code,
                        material: item.material,
                        unit: item.unit,
                        qty: item.qty,
                        errors: {
                                'code': error['code'] || '',
                                'material': error['material'] || '',
                                'qty': error['qty'] || ''
                        } 
                    }
                    this.items.push(new_item);
                    console.log(';itempuhcado')
                    console.log(item)
                        
                }
                    
            }else if(itemsFromForm!=undefined){
                this.items.push({ code: '', material: '', unit: '', qty: 0, errors:'' });
            }

             
        },
          
        

        addItem() {
            this.items.push({ code: '', material: '', unit: '', qty: 0, errors:'' }); // Agrega un nuevo material
        },

        removeItem(index) {
            this.items.splice(index, 1); // Elimina el material por índice
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
                            this.items[index]['material'] = 'Codigo no existe'
                        }
                        else{
                            this.items[index]['material'] = data[0].name
                            this.items[index]['unit'] = data[0].unit
                        }
                        
                        //console.log(this.items[index]['material'])
                    });
            }
        }
    }
}