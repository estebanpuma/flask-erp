function lotForm(preselectedMaterialId = null) {
  return {
    form: {
      lot_number: '',
      material_id: preselectedMaterialId || '',
      warehouse_id: '',
      quantity: '',
      notes: '',
      supplier_id: '',
    },
    materials: [],
    filteredMaterials: [],
    warehouses: [],
    unit: '',
    loading: false,
    success: false,
    error: '',
    locked: preselectedMaterialId !== null,
    searchQuery: '',

    supplierQuery: '',
    suppliers: [],
    filteredSuppliers: [],
    selectedSupplier: null,    // objeto proveedor seleccionado

    init() {
      this.fetchMaterials();
      this.fetchWarehouses();
      this.loadSuppliers();
    },

    async fetchMaterials() {
      try {
        const res = await fetch('/api/v1/materials')
        const data = await res.json()
        this.materials = data
        this.filteredMaterials = data

        // Si está bloqueado, asignar unidad automáticamente
        if (this.locked) {
          const selected = this.materials.find(m => m.id === this.form.material_id)
          if (selected) this.unit = selected.unit
        }
      } catch (err) {
        console.error('Error cargando materiales', err)
      }
    },

    async fetchWarehouses() {
      try {
            const res = await fetch('/api/v1/inventory/warehouses')
            const data = await res.json()
            this.warehouses = data
        } catch (err) {
            console.error('Error cargando bodegas', err)
        }
        },

    updateUnit() {
        const selected = this.materials.find(m => m.id === parseInt(this.form.material_id))
        if (selected) {
            this.unit = selected.unit
        } else {
            this.unit = ''
        }
        },

    filterMaterials() {
        const q = this.searchQuery.toLowerCase()

        this.filteredMaterials = this.materials.filter(m =>
            m.name.toLowerCase().includes(q) || m.code.toLowerCase().includes(q)
        )
        },


    async loadSuppliers() {
        try {
            const res = await fetch('/api/v1/suppliers');
            const data = await res.json();
            this.suppliers = data;

        } catch (err) {
            console.error('Error al cargar proveedores', err);
        }
        },

    filterSuppliers() {
        const q = this.supplierQuery.toLowerCase();
        this.filteredSuppliers = this.suppliers.filter(s => {
            const name = s.name?.toLowerCase() || '';
            const ruc = s.ruc_or_ci?.toLowerCase() || '';
            return name.includes(q) || ruc.includes(q);
        });
        },


    async submit() {
        this.loading = true
        this.success = false
        this.error = ''

        try {
            const res = await fetch('/api/v1/material-lots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.form),
            })

            if (!res.ok) {
            const data = await res.json()
            throw new Error(data.message || 'Error al guardar')
            }

            this.success = true
            setTimeout(() => {
            window.location.href = '/materials/' + this.form.material_id + '/lots'
            }, 1000)
        } catch (err) {
            console.error(err)
            this.error = err.message
        } finally {
            this.loading = false
        }
        },


  }
}
