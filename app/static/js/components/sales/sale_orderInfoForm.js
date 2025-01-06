function sale_orderInfoForm(){
    return{
        order:{
            order_number:'',
            request_date:'',
            delivery_date:'',
            salesperson:''
        },

        orderErrors:{
            order_number:[],
            request_date:[],
            delivery_date:[],
            salesperson:[]
        },
        users:[],

        today: new Date(),

        async init(){
            await this.fecthSalespersons()
            
        },

   

        async loadFormData(data){
            console.log(data)
            if(data){
                console.log('hasy daa')
                this.order.order_number = data.order_number || '';
                this.order.request_date =new Date( data.request_date || this.today).toISOString().split("T")[0] ;
                this.order.delivery_date = data.delivery_date ? new Date(data.delivery_date).toISOString().split("T")[0] : '';
                this.order.salesperson = data.salesperson || '';
            }
        },

        async loadFormErrors(errors){
            
            if(errors){
                console.log('entra error')
                this.orderErrors.order_number.push(errors.order_number || []);
                this.orderErrors.request_date.push(errors.request_date || []);
                this.orderErrors.delivery_date.push(errors.delivery_date || []);
                this.orderErrors.salesperson.push(errors.salesperson || []);
            }
        },

       

        async fecthSalespersons(){
            try{
                const response = await fetch('/api/v1/users?q=salesperson');
                if(response.ok){
                    const salespersons = response.json()
                    console.log(salespersons)
                    this.users = salespersons
                }
            }catch{
                console.log(error);
            }
        }
    }
}