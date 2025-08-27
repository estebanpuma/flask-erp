function salesWizard(){
    return{
        // Estado general
        step: 1,
        taxes: 15,
        totalSteps: 8,
        loading: false,
        error: null,
        temp_lines:[],

        order:{
            order_number:'',
            request_date:'',
            due_date:'',
            salesperson:'',
            notes:'',
        }, 
        shipping:{
            province_id: '',
            canton_id: '',
            address: '',
            reference: '',
            cost:5,
        },
        customer:{},
        payment:{},
        
        designs_request:[],

        // Búsquedas
        subtotal:0,
        total:0,
        //cliente
        customerQuery: '',
        customerResults: [],
        //catalogo
        productQuery: '',
        //pagos
        payment_methods: [],
        design_order:{
            lines:[],
            subtotal:[]
        },
        //Diseño & Variante
        selectedProduct: null,
        designs: [],
        selectedDesign: null,
        variants: [],
        //datos generales
        salespersons: [],

        // Utilitarios genéricos
        async fetcher(method, path, body = null) {
        this.loading = true;
        this.error = null;
        try {
            const opts = { method, headers: { 'Content-Type': 'application/json' } };
            if (body) opts.body = JSON.stringify(body);
            const res = await fetch(`/api/v1/${path}`, opts);
            if (!res.ok) throw new Error(`${res.status} ${res.statusText} ${await res.message}`);
            return await res.json();
        } catch (e) {
            this.error = e.message;
            return null;
        } finally {
            this.loading = false;
        }
        },

//----------------------------------------------------------------------------
//----------------------------Cliente-----------------------------------------
        async searchCustomers() {
            this.customerResults = [];
            if(this.customerQuery.length>2){
                this.customerResults = await this.fetcher('GET', `clients/search?q=${encodeURIComponent(this.customerQuery)}`) || [];

            }
        },
        
        clearCustomerSearch() {
            this.customerQuery = '';
            this.customerResults = [];
        },
        selectCustomer(c) {

            this.customer = c;
            this.shipping.province_id = this.customer.province_id;
            this.shipping.canton_id = this.customer.canton_id;
            this.shipping.address = this.customer.address;
            this.clearCustomerSearch();
        },

        openNewCustomer() {
            // Abre el offcanvas del formulario de nuevo cliente
            let instance = bootstrap.Offcanvas.getOrCreateInstance(this.$refs.customerOffcanvas);
            instance.show();
        },

        async saveNewCustomer() {
            // Intenta guardar el nuevo cliente
            const c = await this.fetcher('POST', 'clients', this.clientForm);
            if (c && c.id) {
                this.customer = c;
                let instance = bootstrap.Offcanvas.getInstance(this.$refs.customerOffcanvas);
                if (instance) instance.hide();
                this.nextStep(); // O navega a donde necesitas
            } else {
                // Aquí podrías mostrar un error visual
                this.newCustomerError = 'No se pudo crear el cliente. Verifica los datos.';
            }
        },
        clientForm: {
            ruc_or_ci: '',
            name: '',
            email: '',
            phone: '',
            address: '',
            client_type: '',
            is_special_taxpayer: false,
            province_id: '',
            canton_id: ''
            },
        provinces: [],
        cantons: [],
        error: null,
        rucError: null,

        async initForm() {

            this.provinces = await this.fetcher('GET', `provinces`);
            this.loadCantons(this.clientForm.province_id);
            
            },

        async loadCantons(province_id) {
            this.cantons = [];
            if (!province_id) return;
            this.cantons = await this.fetcher('GET',`cantons?province_id=${province_id}`);
        },

        async validateRUC() {
            this.rucError = null;
            if (!this.clientForm.ruc_or_ci || this.clientForm.ruc_or_ci.length < 10) return;
            let client = await this.fetcher('GET', `clients?ruc_or_ci=${this.clientForm.ruc_or_ci}`)
            if(client.ruc_or_ci) this.rucError = 'Ya existe un cliente con esta cédula/RUC';                      
        },

//---------------------------------------------------------------------------------
//-------------------------------Catálogo-------------------------------------------
        async fetchProduct(d){
            console.log('dp', d)
            this.selectedProduct ='',
            this.selectedProduct = await this.fetcher('GET', `products/${d}`)
        },

        async fetchDesigns(){
            this.designs =[],
            this.designs = await this.fetcher('GET', `product-designs`)
        },

        async searchDesigns() {
            let designs = await this.fetcher('GET', `product-designs?search=${encodeURIComponent(this.productQuery)}`) || [];
            if(designs.length>0){
                this.designs = designs;
            }else{
                this.designs = this.fetchDesigns();
            }
        },
        
        async selectDesign(id) {
            let design = await this.fetcher('GET', `product-designs/${id}`) || [];
            this.selectedDesign = design      // espera que el API devuelva p.designs = [{id, code, color, variants:[...]}, …]
            this.variants = design.variants;
            this.onDesignChange()
            this.selectedVariant = null;
            this.step = 2;        
              // avanza directo al paso 2
            },

        
            //imgane principal
        getPrimaryImageUrl(images) {
            if (!images || images.length === 0) {
            return '/static/media/not_found_img.jpg'; // Opcional, por si no hay imágenes
            }
            // Busca la primaria
            const primary = images.find(img => img.is_primary);
            // Retorna la url de la primaria o la primera
            return primary
            ? `/api/v1/media/img/designs/${primary.filename}`
            : `/api/v1/media/img/designs/${images[0].filename}`;
        },

        // 3. Variante & carrito

        incrementVariant(v){
            console.log('incement',v)
            if(v.quantity===null || v.quantity===''){
                v.quantity = 0
            }
            v.quantity = v.quantity + 1
            this.updateLine(v)
        },
        decrementVariant(v){
            console.log('decrement', v)
            v.quantity = v.quantity - 1
            this.updateLine(v)
        },

            // — Paso 3: Diseño & Variante —
        onDesignChange() {
            this.variants = this.selectedDesign.variants || [];
            this.design_order = {
                lines:[],
                subtotal:0
                };

            let design = this.designs_request.find(d => d.id === this.selectedDesign.id);

            this.variants.forEach(variant => {
                variant.quantity = 0
                variant.current_price = Number(this.selectedDesign.current_price)
                
                if (design){
                    let line = design.lines.find(l => l.variant_id === variant.id)
                
                    if(line){
                        variant.quantity = line.quantity
                        variant.current_price = Number(this.selectedDesign.current_price)

                        this.design_order.lines.push({
                            'variant_id': line.variant_id,
                            'quantity': line.quantity

                        })
                        
                        
                    } 
  
                }
            
            });
            
        },



        lineSubtotal(){
           
            let design_subtotal = this.designSubtotal(this.design_order)
            return design_subtotal
        },

        designSubtotal(design){
            
            let design_subtotal = design.lines.reduce((accumulator, line)=>{
                subtotal = (accumulator +(line.quantity * decimalUtils.toCents(this.selectedDesign.current_price)))
                return subtotal
            },0)
            return decimalUtils.moneyFormat(decimalUtils.fromCents(design_subtotal));

        },

        updateLine(v){
            const idx = this.design_order.lines.findIndex(l => l.variant_id === v.id);
            if (v.quantity > 0) {
                if (idx !== -1) {
                    this.design_order.lines[idx].quantity = v.quantity;
                    
                } else {  
                    this.design_order.lines.push({
                    design: this.selectedDesign,
                    variant_id: v.id,
                    quantity: v.quantity,
                    code: v.code
                });
                }
            } else if (idx !== -1) {
                // Si la cantidad bajó a 0, eliminamos sólo esa línea
                this.design_order.lines.splice(idx, 1);
            }
           this.lineSubtotal()
        },

        saveLine(v) {
            // Buscar el diseño por ID
            let targetId = this.selectedDesign.id;
            let design = this.designs_request.find(d => d.id === targetId);

            // Si no existe el diseño, lo creas
            if (!design) {
                design = {
                    id: targetId,
                    design: this.selectedDesign,
                    lines: [],
                    subtotal: 0
                };
                this.designs_request.push(design);
            }

            // Ahora buscas la línea (variante) en ese diseño
            let line = design.lines.find(l => l.variant_id === v.id);

            if (v.quantity > 0) {
                if (line) {
                    // Actualizar cantidad y subtotal
                    line.quantity = v.quantity;
                    line.subtotal = decimalUtils.fromCents(v.quantity * decimalUtils.toCents(this.selectedDesign.current_price));
                    line.code = v.code;
                } else {
                    // Agregar nueva línea
                    design.lines.push({
                        variant_id: v.id,
                        code: v.code,
                        quantity: v.quantity,
                        subtotal: decimalUtils.fromCents(v.quantity * decimalUtils.toCents(this.selectedDesign.current_price)),
                    });
                }
            } else if (line) {
                // Si la cantidad es 0, elimina la línea de variantes
                design.lines = design.lines.filter(l => l.variant_id !== v.id);
            }

            // Si después de todo, el diseño NO tiene líneas, lo eliminamos del array
            if (design.lines.length === 0) {
                // Remover de designs_request por id
                this.designs_request = this.designs_request.filter(d => d.id !== targetId);
            } else {
                // Si sigue teniendo líneas, actualiza el subtotal
                design.subtotal = design.lines.reduce((sum, l) => sum + l.subtotal, 0);
            }

            this.updateSubtotal();
        },

        addToCart() {
            this.variants.forEach(v => {
                this.saveLine(v);
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
           
        },


        async updateSubtotal() {
            this.loadingSubtotal = true;
            this.errorSubtotal = null;

            try {
                // Junta todas las líneas de todos los diseños
                let lines = [];
                this.designs_request.forEach(design => {
                    design.lines.forEach(line => {
                        lines.push({
                            variant_id: line.variant_id,
                            quantity: line.quantity
                        });
                    });
                });

                let subpayload = { lines };

                // Puedes mostrar loader en el frontend con this.loadingSubtotal
                let response = await this.fetcher('POST', `/sale-orders/preview`, subpayload);

                if (response && typeof response.subtotal !== 'undefined') {
                    this.subtotal = await response.subtotal;
                    console.log('updated subtotal: ', response.subtotal)
                    this.total = await response.total

                    return this.subtotal
                } else {
                    this.subtotal = 0;
                    this.errorSubtotal = "No se pudo calcular el subtotal. Verifique los datos del pedido.";
                }
            } catch (err) {
                this.subtotal = 0;
                this.errorSubtotal = "Error al calcular subtotal: " + (err.message || err);
                console.error(err);
            } finally {
                this.loadingSubtotal = false;
            }
        },



        removeFromCart(line, design) {
                // Filtra la línea que quieres quitar
                design.lines = design.lines.filter(l => l.variant_id !== line.variant_id);

                // Recalcula el subtotal del diseño
                design.subtotal = design.lines.reduce((sum, l) => sum + l.subtotal, 0);

                // Si ya no quedan líneas, puedes (opcional) quitar el diseño completo del carrito
                this.designs_request = this.designs_request.filter(d => d.lines.length > 0);

                this.updateSubtotal();
            },

        calculateTotal(subtotal=this.subtotal, shipping=this.shipping.cost, taxes=this.taxes){
            let total = ((decimalUtils.toCents(subtotal) + decimalUtils.toCents(shipping))+((decimalUtils.toCents(subtotal) + decimalUtils.toCents(shipping))*(taxes/100))).toFixed(2)

            this.total = decimalUtils.fromCents(total)
            return this.total
        },
                    


//-----------------------------OrderData------------------------------
        today() {
            const d = new Date();
            return d.toISOString().split('T')[0];
        },

        futureDay(days = 15){
            const d = new Date();
            d.setDate(d.getDate() + days)
            return d.toISOString().split('T')[0];
        },

        async fetchSalesPersons(){
            
            this.salespersons = await this.fetcher('GET', '/workers')
        },

        calculatePendingAmount(total, paid){

            let pending_amount = decimalUtils.toCents(total) - decimalUtils.toCents(paid)
            console.log('pendig amount: ', pending_amount)
            return decimalUtils.moneyFormat(decimalUtils.fromCents(pending_amount));
          
        },
            
        async fetchPaymentMethods(){
            this.payment_methods = await this.fetcher('GET', 'payment-methods')
        },

        clearError(){
            this.error = '';
        },

        // Navegación
        nextStep() {
            
            if (this.step === 6){
                this.clearError();
                if(!this.shipping.address || !this.shipping.province_id || !this.shipping.canton_id){
                    console.error('no se puede enviar vacio')
                    this.error= 'Debes completar todos los datos de envío.'
                    return
                }
                
            }
            if (this.step < this.totalSteps) this.step++;
            //if (this.step === this.totalSteps) this.confirmOrder()
       
        },
        prevStep() {
            if (this.step > 1) this.step--;
        },

        printSection(sectionId) {
            const printContents = document.getElementById(sectionId).innerHTML;
            const originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload(); // recarga Alpine si usas datos reactivos
            },
        
        formLoading: false,
        async confirmOrder(){
            this.formLoading = true
            let order_lines = []
            this.designs_request.forEach(design=>{
                design.lines.forEach(line =>{
                    order_lines.push({
                        'variant_id': line.variant_id,
                        'quantity': line.quantity,
                    })
                })
            })
            const payload = {
                order_number: this.order.order_number,
                order_date: this.order.request_date,
                due_date: this.order.due_date,
                client_id: this.customer.id,
                sales_person_id: this.order.salesperson,
                notes: this.order.notes,
                lines:order_lines,
                
                shipping_province_id: this.shipping.province_id,
                shipping_canton_id: this.shipping.canton_id,
                shipping_address: this.shipping.address,
                shipping_reference: this.shipping.reference,
                
                payment:{
                    amount: this.payment.amount,
                    method_id:this.payment.method_id,
                    date:this.order_date
                }
            }
            console.log('ave a ver')
            console.log(payload)
            this.submitSale(payload)

        },

        // Finalizar
        async submitSale(payload) {
            try{
                const res = await this.fetcher('POST', 'sale-orders', payload);
                if (res) {
                alert('exitaso')

                }
                this.formLoading = false
            }catch(error){
                console.error(error)
                this.formLoading = false
                alert(error)

            }
            
            
        },
    }
}


    