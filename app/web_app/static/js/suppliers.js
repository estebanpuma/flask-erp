function supplierForm() {
  return {
    form: {
      name: '',
      ruc_or_ci: '',
      email: '',
      phone: '',
    },
    loading: false,
    success: false,
    error: '',

    init() {
      this.success = false;
      this.error = '';
    },

    async submit() {
      this.loading = true;
      this.success = false;
      this.error = '';

      try {
        const res = await fetch('/api/v1/suppliers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.form),
        });

        const data = await res.json();
        
        if (!res.ok) {
          throw new Error(data.message || 'Error al guardar proveedor');
        }

        this.success = true;
        this.form = { name: '', ruc_or_ci: '', email: '', phone: '' };
        const parent = document.querySelector('[x-ref="materialLotForm"]');
        if (parent && parent.__x) {
        parent.__x.$data.form.supplier_id = data.id;
        parent.__x.$data.selectedSupplier = data;
        }
        // Aquí podrías cerrar el offcanvas automáticamente si quieres:
        const offcanvasEl = document.getElementById('newSupplierOffcanvas');
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
        
        console.log('data:', data)
        
                    
        // TODO: Emitir evento personalizado o actualizar proveedor en el formulario principal
      } catch (err) {
        this.error = err.message;
      }

      this.loading = false;
    },
  };
}
