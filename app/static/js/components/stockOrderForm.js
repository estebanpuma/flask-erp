function stockOrderForm(){
    
    return{
        // Datos iniciales
        
        item: {
            code: '',
            request_date: '',
            responsible: '',
            notes: '',
        },
        items: [],
        itemErrors: {
                    code:[],
                    request_date:[],
                    responsible:[],
                    notes:[],
                    items:[]
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
        },

        async searchSize(){
            console.log('ya va a buscar')
        },

        async searchModel(code){
            
            try{
                const response = await fetch(`/api/v1/products?code=${code}`)
                console.log(response)
                
                if(response.ok){
                    let model = await response.json()
                    console.log(model)
                    
                }else if(response.status == 404){
                    console.log('No existe')
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
                const response = await fetch('/api/v1/get-next-stock-code')
                if(response.ok){
                    this.item.code = await response.json()
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
                    const fields = formData?.fields || {};
                    const errors = formData?.errors || {};
                    

                    this.item = {
                        code: fields.code || '',
                        request_date: fields.request_date 
                                        ? new Date(fields.request_date).toISOString().split('T')[0] 
                                        : new Date().toISOString().split('T')[0],
                        responsible: fields.responsible || '',
                        notes: fields.notes ||'',
                    };
                    this.itemErrors = {
                        code: errors.code || [],
                        request_date: errors.request_date || [],
                        responsible: errors.responsible || [],
                        items: errors.items || {}
                    };
                    console.log('this are item: ',this.item)
                    console.log('this is itemErrors after:',this.itemErrors)
                    this.initItems(fields?.items || [], errors?.items || []);
                }catch(error){
                    console.error("Error inicializando el formulario:", error);
                };
            };

        },

        initItems(items, errors){
            console.log('items: ', items)

            console.log('errors: ', errors)
            if(items.length>0){
                console.log('pasa alidate items')
                this.items = items.map(item => ({
                    code: item.code || '',
                    size: item.size || '',
                    qty: item.qty || 0
                }));

                this.itemErrors.items = errors.map(error=>({
                    code: error.code || [],
                    size: error.size || [],
                    qty: error.qty || []
                }));
                console.log('itemsErrors.items: ', this.itemErrors.items)
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
                    console.log(fetchusers)
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