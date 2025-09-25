function warehousesForm() {
  return {
    loading: false,
    form: {
      name: '',
      code:'',
      description: '',
      location:'',
    },
    message: '',
    success: false,
    errors:'',
    existing_code:false,
    existing_name:false,


    init() {
      // Opcional: lógica inicial
    },

    async checkCode(){
        try{
            const res = await fetch(`/api/v1/warehouses?code=${this.form.code.toUpperCase()}`);
            const data = await res.json()
            this.existing_code = false;
            if (data!==null && data[0].code){
                this.existing_code = true;
                return true
                }
                else{
                this.existing_code = false;
                return false
                }
        }catch(err){
            console.error()
            this.message = err.toString()
        }
    },

    async checkName(){
        try{
            const res = await fetch(`/api/v1/warehouses?name=${this.form.name}`);
            const data = await res.json()
            if (data.code){
                this.existing_name = true;
                return true
                }
                else{
                this.existing_name = false;
                return false
                }
        }catch(err){
            console.error()
            this.message = err.toString()
        }
    },


    async submitForm() {
      this.loading = true;
      this.message = '';
      try {
        const res = await fetch('/api/v1/warehouses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form),
        });
        const data = await res.json();
        this.success = res.ok;
        this.message = this.success ? '✅ Grupo creado' : (data.message || '❌ Error al crear grupo');
        if (this.success) {
          this.form.name = '';
          this.form.code = '';
          this.form.description = '';
          alert(this.message)
          window.location.href = '/warehouses';
        }else{
          this.success = false;
        this.message = '❌ Error de conexión';
        console.log(this.message)
        }
      } catch (err) {
        console.error(err);
        this.success = false;
        this.message = '❌ Error de conexión';
        console.log(this.message)
      } finally {
        this.loading = false;
      }
    }
  }
}
