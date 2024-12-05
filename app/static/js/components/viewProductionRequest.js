function viewProductionRequest(production_request_id){
    return{
        request:{
                type:'',
                order_number:"",
                responsible:"",
                request_date:"",
                notes:""
        },

        models:[{
                code:"",
                qty:"",
                size:""
        }],

        badgeClasses: {
            'Pendiente': 'badge rounded-pill text-bg-danger',
            'Completada': 'badge rounded-pill text-bg-success',
            'En proceso': 'badge rounded-pill text-bg-primary',
            'Programada': 'badge rounded-pill text-bg-warning'
        },

        async init(id = production_request_id){
            try{
                const response = await fetch(`/api/v1/production_requests/${id}`);

                if(response.ok){
                    const request = await response.json();
                    console.log(request);
                    console.log(request.order_number)
                    this.request = {
                                    type: request.order_type,
                                    status: request.status,
                                    order_number: request.order_number,
                                    responsible: request.responsible,
                                    notes: request.notes,
                                    request_date: request.request_date
                    }

                    this.models = []
                    request.models.forEach(model => {
                        this.models.push(model)
                    });
                    console.log('models:', this.models)
                }
            }catch(error){
                console.log(error)
            }
        }
    }
}