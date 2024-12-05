function stockOrderForm(){
    
    return{
        // Datos iniciales
        
        item: {
            code: '',
            request_date: '',
            delivery_date:'',
            responsible: '',
            notes: '',
        },
        items: [],
        itemErrors: {
                    code:[],
                    request_date:[],
                    delivery_date:[],
                    responsible:[],
                    notes:[],
                    items:[{ code: [], size: [], qty: [] }]
        },
        
        users: [],

        addItem(){
            this.items.push({
                code:'',
                code_check:'',
                size:'',
                qty:0
            })
            this.itemErrors.items.push({ code: [], size: [], qty: [] });
        },

        removeItem(index){
            this.items.splice(index,1)
            this.itemErrors.items.splice(index,1)
        },

        async searchSize(size, index){
            try{
                const response = await fetch(`/api/v1/sizes?value=${size}`)
                if(response.ok){
                    let size = await response.json()
                    console.log(size)
                }else{
                    this.itemErrors.items[index].size.push('Talla no existe')
                }
            }catch(error){
                console.log(error)
            }
            
        },

        async searchModel(code, index){
            
            try{
                const response = await fetch(`/api/v1/products?code=${code}`)
                console.log(response)
                
                if(response.ok){
                    let model = await response.json()
                    this.items[index].code_check = true;
                    console.log('this codecheck', this.items.code_check)
                    
                }else if(response.status == 404){
                    this.items[index].code_check = false;
                }
                else{
                    
                    console.log('Ocurrio un erro (fech model)')
                }
            }catch(error){
                console.log(error)
            }
        },

       
        async getNextCode(){
            try{
                console.log('ingresa a get next code')
                const response = await fetch('/api/v1/get-next-stock-code')
                if(response.ok){
                    let next_code = await response.json()
                    this.item.code = next_code
                    console.log('this is next code', next_code, 'vs ', this.item.code, typeof(this.item.code))
                }else{
                    console.log('ocrrio un error')
                }
            }catch(error){
                console.log(error)
            }
        },

        
        async init(formData){
            
            if(formData!==undefined){
                console.log('Inicializando stockOrderForm...', formData);
                console.log('Item errors before:', this.itemErrors)
                try{
                    await this.fecthUsers();
                    await this.getNextCode();
                }catch(error){
                    console.log('Ocurrio un error cargando datos: ',error)
                };
                try{
                    
                    const fields = formData?.fields || {};
                    const errors = formData?.errors || {};
                    

                    this.item = {
                        code: fields.code || this.item.code,
                        request_date: fields.request_date 
                                        ? new Date(fields.request_date).toISOString().split('T')[0] 
                                        : new Date().toISOString().split('T')[0],
                        delivery_date: fields.delivery_date || '',
                        responsible: fields.responsible || '',
                        notes: fields.notes ||'',
                    };
                    this.itemErrors = {
                        code: errors.code || [],
                        request_date: errors.request_date || [],
                        request_date: errors.delivery_date || [],
                        responsible: errors.responsible || [],
                        items: errors.items || []
                    };
                   
                    console.log('this is itemErrors after:',this.itemErrors.items)
                    this.initItems(fields?.items || [], errors?.items || []);
                }catch(error){
                    console.error("Error inicializando el formulario:", error);
                };
            };

        },

        initItems(items, errors){
            
            if(items.length>0){
                try{
                    this.items = items.map(item => ({
                        code: item.code || '',
                        size: item.size || '',
                        qty: item.qty || 0
                    }));
                    if(errors.length>0){
                        this.itemErrors.items = errors.map(error=>({
                            code: error.code || [],
                            size: error.size || [],
                            qty: error.qty || []
                        }));
                    }else{
                        this.itemErrors.items = [{ code: [], size: [], qty: [] }];
                    }
                }catch(error){
                    console.log('Ocurrio un error: ', error)
                }
            }else{
                this.items = [{ code: '', size: '', qty: 0 }];
                this.itemErrors.items = [{ code: [], size: [], qty: [] }];
            }
        },

        async fecthUsers(){
            try{
                const response = await fetch('/api/v1/users')
                if(response.ok){
                    let fetchusers = await response.json()
                    this.users = fetchusers
                }else{
                    console.log('ocurrio un error con users')
                }
            }catch(error){
                console.log(error)
            }
        },

        

    }
}