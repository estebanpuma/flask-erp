function viewProductionOrder(id){
    return{
        order:[{
            id:'',
            code:'',
            scheduled_start_date:'',
            scheduled_end_date:'',
            status:'',
        }],

        requests: [],

        items: [],
        
        totals: {
            qty:  0
        },

        badgeClasses: {
            'Pendiente': 'badge rounded-pill text-bg-danger',
            'Completada': 'badge rounded-pill text-bg-success',
            'En proceso': 'badge rounded-pill text-bg-primary',
            'Programada': 'badge rounded-pill text-bg-warning'
        },

        async init(){
            try{
                const response = await fetch(`/api/v1/production_orders/${id}`);
                if(response.ok){
                    const p_order = await response.json();
                    this.order = p_order;
                    await this.getUsername(p_order.responsible_id)
                    const requests = p_order.production_requirements
                    requests.forEach(request => {
                        const order_request = this.getProductionRequests(request.id);
                        this.requests.push(order_request);
                    });
                    const items = await this.fecthProductionDetail(id);
                    let cont = 0;
                    let total_items = items.length;
                    items.forEach(item =>{
                        cont = cont+ 1
                        let viajera = cont + '-' + total_items
                        const new_item = {
                            code:item.model_code,
                            size:item.size,
                            series:item.series,
                            qty:item.total_quantity,
                            batch: viajera
                        }
                        this.items.push(new_item)
                    })
                    
                    console.log('este es requ: ', this.requests)
                    console.log('este es items: ', this.items)
                    const total = this.items.reduce((sum, item) => sum + item.qty, 0);
                    this.totals.qty = total;
                    console.log('Total Quantity:', this.totals.qty); // Output: 30
                }

            }catch(error){
                console.log(error);
            }
        },

        async getUsername(user_id){
            try{
                const response = await fetch(`/api/v1/users/${user_id}`);
                if(response.ok){
                    const user = await response.json()
                    this.order.responsible = user.username;
                    console.log(this.order)
                }
            }catch(error){
                console.log(error)
            }
        },

        async fecthProductionDetail(id){
            try{
                console.log(id)
                const response = await fetch(`/api/v1/production_orders/${id}/items`)
                if(response.ok){
                    const items = await response.json()
                    console.log(items)
                    return items
                }
            }catch(error){
                console.log(error)
            }
        },

        async getProductionRequests(id){
            try{
                console.log(id)
                const response = await fetch(`/api/v1/production_requests/${id}`)
                if(response.ok){
                    const requests = await response.json()
                    console.log(requests)
                    return requests
                }
            }catch(error){
                console.log(error)
            }
        }
    }
}