function viewProductionOrders(){
    return{
        orders:[{
            id:'',
            code:'',
            scheduled_start_date:'',
            scheduled_end_date:'',
            status:'',
        }],

        async init(){
            try{
                const response = await fetch('api/v1/production_orders')
                if(response.ok){
                    const p_orders = await response.json()
                    this.orders = []
                    p_orders.forEach(order => {
                        this.orders.push(order)
                    });
                    console.log(this.orders)
                }
            }catch(error){
                console.log(error)
            }
        },

        redirect_order(id){
            
            const url = `/production_orders/${id}`;
            window.location.href = url;
            
        }
    }
}