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

        models: [],

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
                    const requests = p_order.production_requirements
                    requests.forEach(request => {
                        const response_request = this.getProductionRequests(request.id)
                        console.log(response_request)
                    });
                    await this.getUsername(p_order.responsible_id)
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