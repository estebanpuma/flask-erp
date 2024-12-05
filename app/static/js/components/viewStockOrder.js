function viewStockOrder(stock_order_id){
    return {
        stock_order:{
                        id:'',
                        code:'',
                        status: '',
                        request_date:'',
                        responsible:'',
                        notes:''              
        },
        
        models:[{
                code:'',
                size:'',
                qty:''
                }],
        
        badgeClasses: {
            'Pendiente': 'badge rounded-pill text-bg-danger',
            'Completada': 'badge rounded-pill text-bg-success',
            'En proceso': 'badge rounded-pill text-bg-primary',
            'Programada': 'badge rounded-pill text-bg-warning'
        },
        
        async init(){
            console.log('init...');
            await this.fecthStockOrder(stock_order_id);
        },

        async fecthStockOrder(stock_order_id){
            try{
                const url = `/api/v1/stock_orders/${stock_order_id}`;
                const response = await fetch(url);
                
                if(response.ok){
                    const stock_order = await response.json();
                    const responsible = await this.fetchUser(stock_order.responsible_id);
                    this.stock_order = {
                                        id:stock_order.id,
                                        code:stock_order.stock_order_code,
                                        status:stock_order.status,
                                        request_date:stock_order.request_date,
                                        responsible:responsible,
                    }
                    await this.loadModels(stock_order.stock_order_product_list);
                }
            }catch(error){
                console.log(error);
            }
        },

        async loadModels(models){
            try{
                models.forEach(element => {
                    console.log(element);
                    const model =  this.fetchModel(element.product_id);
                    this.models.push({code:model,
                                        size:element.product_size,
                                        qty:element.product_qty
                    });
                });
            }catch(error){
                console.log(error);
            }
        },
        
        async fetchModel(model_id){
            try{
                const response = await fetch(`/api/v1/products/${model_id}`);
                if(response.ok){
                    const model = await response.json();
                    return model.code;
                }else{
                    console.log('error al cargar modelo');
                }

            }catch(error){
                console.log(error);
            }
        },

        async fetchUser(user_id){
            try{
                const response = await fetch(`/api/v1/users/${user_id}`);
                if(response.ok){
                    const user = await response.json();
                    console.log(user.username);
                    return user.username;
                }else{
                    console.log('error al cargar resposable');
                }
            }catch(error){
                console.log(error);
            }
        },
        

    }
}