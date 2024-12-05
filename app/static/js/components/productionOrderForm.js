function productionOrderForm(){
    return{
        order:{
            order_number:'',
            scheduled_start_date:'',
            scheduled_end_date:'',
            responsible:'',
            notes:''
        },

        orderErrors:{
            order_number:[],
            scheduled_start_date:[],
            scheduled_end_date:[],
            responsible:[],
            notes:[],
            items:[]
        },

        users:[],

        items:[],

        selectedItems: [],

        async init(){
            try {
                await this.fetchUsers();
                console.log('carga users')
                await this.fetchProductionRequests();
                console.log('fin iitnit:', this.order)
            } catch (error) {
                console.error('Error al inicializar el componente:', error);
            }

            
        },

        loadForm(form){
            console.log('inicia load form')
            console.log(form)
            try{
                this.order = {
                    order_number: this.getOrdenNumber(),
                    scheduled_start_date: form.scheduled_start_date 
                                        ? new Date(form.scheduled_start_date ).toISOString().split('T')[0] 
                                        : new Date().toISOString().split('T')[0],
                    scheduled_end_date:form.scheduled_end_date 
                                        ? new Date(form.scheduled_end_date ).toISOString().split('T')[0] 
                                        : '',
                    responsible:parseInt(form.responsible)||'', 
                    notes:form.notes||''
                }
                console.log('new order:', this.order)
            }catch(error){
                console.log(error)
            }
            try{
                const items =  form.items
                 // Marcar elementos seleccionados
                 items.forEach(item => {
                    if(item.is_selected){
                        this.selectedItems.push(item.request_id)
                    }
                 });
                 console.log('selected', this.selectedItems);

            }catch(error){
                console.log(error);
            }
        },


        async getOrdenNumber(){
            try{
                const response = await fetch('/api/v1/production_orders/next_code');
                if(response.ok){
                    const code =await response.json();
                    this.order.order_number=code;
                    return code;
                }
            }catch(error){
                console.log(error);
            }
        },


        async fetchProductionRequests(){
            try{
                console.log('init items dese fetch')
                const response = await fetch('/api/v1/production_requests');
                if(response.ok){
                    const requests = await response.json();
                    requests.forEach(request => {
                        if(request.status==='Pendiente'){
                            itemrequested = {
                                id:request.id,
                                is_selected:false,
                                request_date: request.request_date,
                                order_type: request.order_type,
                                order_number: request.order_number,
                                status: request.status
                            }
                            this.items.push(itemrequested);
                        }
                        
                    });
                    console.log('itmes: ', this.items, 'fin fecth itmes');
                }
            }catch(error){
                console.log(error);
            }
        },

        async fetchUsers(){
            console.log('cargando usuarios')
            try{
                const response = await fetch('/api/v1/users');
                if(response.ok){
                    const users = await response.json();
                    this.users = users;
                }
            }catch(error){
                console.log(error)
            }
        }


    }
}