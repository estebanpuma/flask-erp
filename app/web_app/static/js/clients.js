function clientsTable() {

  return {
    clients: [],
    loading: true,
    error: null,
    selectedClient: null,

    init() {
      // Escuchar evento global personalizado
      window.addEventListener('client-selected', (e) => {
        this.selectedClient = e.detail;
        console.log('Cliente seleccionado:', this.selectedClient);

        window.location.href = `/clients/${this.selectedClient.id}`;

      });
    },

    async fetchClients() {
      try {
        this.loading = true;
        const res = await fetch('/api/v1/clients'); // ajusta si tu ruta es diferente
        const data = await res.json();
        console.log(data)
        if (!res.ok) throw new Error(data.message || 'Error al cargar clientes');
        this.clients = data;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
}


function clientForm(client_id=null) {
  return {
    client_id,
    form: {
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
    successMessage: null,
    rucError: null,
    isEdit: false,

    async initForm() {
      if(client_id!==null && client_id>0){
        this.isEdit = true
        try{
          const res = await fetch(`/api/v1/clients/${client_id}`);
          const data = await res.json();
          this.form = data;
          this.form['province_id']=data.province.id

          this.form['canton_id']=data.canton.id

          console.log(this.form)
        } catch(err){
          this.error = 'Error al cargar cliente';
        }
      };
      try {
        const res = await fetch('/api/v1/provinces');
        const data = await res.json();
        this.provinces = data;
        console.log(data)
      } catch (err) {
        this.error = 'Error al cargar provincias';
      };
      this.loadCantons()

    },

    async loadCantons() {
      this.cantons = [];
      //this.form.canton_id = '';
      if (!this.form.province_id) return;

      try {
        const res = await fetch(`/api/v1/cantons?province_id=${this.form.province_id}`);
        const data = await res.json();
        this.cantons = data;
        console.log('cantons',data)
      } catch (err) {
        this.error = 'Error al cargar cantones';
      }
    },

    async validateRUC() {
      this.rucError = null;
      if (!this.form.ruc_or_ci || this.form.ruc_or_ci.length < 10) return;

      try {
        const res = await fetch(`/api/v1/clients?ruc_or_ci=${this.form.ruc_or_ci}`);

        if (res.ok) {
            const data = await res.json();
            console.log(data)
            console.log(data.items)
            if(data.length>0){
                this.rucError = 'Ya existe un cliente con esta cédula/RUC';
            }

        }
      } catch (err) {
        this.rucError = 'No se pudo validar el RUC'+err;
      }
    },

    async submitForm() {
      this.error = null;
      this.successMessage = null;

      if (this.rucError) {
        this.error = 'Corrija los errores antes de continuar';
        return;
      }
      const url = this.isEdit
        ? `/api/v1/clients/${this.clientId}`
        : `/api/v1/clients`;
      const method = this.isEdit ? 'PATCH' : 'POST';

      try {
        const res = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.message || 'Error al guardar cliente');

        this.successMessage = this.isEdit
          ? 'Cliente actualizado correctamente'
          : 'Cliente creado correctamente';

        this.form = {
          ruc_or_ci: '',
          name: '',
          email: '',
          phone: '',
          address: '',
          client_type: '',
          is_special_taxpayer: false,
          province_id: '',
          canton_id: ''
        };
        this.cantons = [];

        setTimeout(() => {
          window.location.href = `/clients/${data.id}`;
        }, 1000);

      } catch (err) {
        this.error = err.message;
      }
    }
  }
}


function clientDetail(client_id) {
  return {
    client_id: null,  // se seteará con Jinja
    client: {},
    loading: true,
    error: null,

    init(){
      console.log('init')
      this.client_id = client_id;
      console.log('client_id: ', client_id)
      this.fetchClient();

      },

    async fetchClient() {
      console.log('inicia fecth')
      try {
        const res = await fetch(`/api/v1/clients/${this.client_id}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || 'Error al cargar cliente');
        this.client = data;
      } catch (err) {
        this.error = err?.message||null;
      } finally {
        this.loading = false;
      }
    },

    goToEdit() {
      const id = this.client.id;
      window.location.href = `/clients/${id}/edit`;
    }
  }
}


function clientEdit(client_id) {
  return {
    clientId: client_id,
    form: {
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
    successMessage: null,
    rucError: null,

    async init() {
      console.log('init')
      try {
        const [clientRes, provinceRes] = await Promise.all([
          fetch(`/api/v1/clients/${this.clientId}`),
          fetch('/api/v1/provinces')
        ]);

        const clientData = await clientRes.json();
        const provinceData = await provinceRes.json();

        if (!clientRes.ok) throw new Error(clientData.message || 'Error al cargar cliente');
        this.provinces = provinceData;
        this.form = clientData;

        await this.loadCantons();
      } catch (err) {
        this.error = err.message;
      }
    },

    async loadCantons() {
      if (!this.form.province_id) return;
      try {
        const res = await fetch(`/api/v1/cantons?province_id=${this.form.province_id}`);
        const data = await res.json();
        this.cantons = data;
      } catch (err) {
        this.error = 'Error al cargar cantones';
      }
    },

    async validateRUC() {
      this.rucError = null;
      if (!this.form.ruc_or_ci || this.form.ruc_or_ci.length < 10) return;

      try {
        const res = await fetch(`/api/clients/validate-ruc?ruc=${this.form.ruc_or_ci}&exclude_id=${this.clientId}`);
        const data = await res.json();
        if (!data.valid) {
          this.rucError = 'Ya existe otro cliente con esta cédula/RUC';
        }
      } catch (err) {
        this.rucError = 'No se pudo validar el RUC';
      }
    },

    async submitForm() {
      this.error = null;
      this.successMessage = null;

      if (this.rucError) {
        this.error = 'Corrija los errores antes de continuar';
        return;
      }

      try {
        const res = await fetch(`/api/clients/${this.clientId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || 'Error al actualizar cliente');

        this.successMessage = 'Cliente actualizado exitosamente';
      } catch (err) {
        this.error = err.message;
      }
    }
  }
}
