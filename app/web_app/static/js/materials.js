
function materialsTable() {
    console.log("JS externo materials.js cargado correctamente");
    return {

        materials: [],
        loading: false,
        error: null,




        fetchMaterials() {
            this.loading = true;
            console.log('iniit fecth')
            fetch('/api/v1/materials')
                .then(res => {
                    if (!res.ok) throw new Error("Error al obtener materiales");
                    return res.json();
                })
                .then(data => {
                    this.materials = data || [];
                    console.log(data)
                })
                .catch(err => {
                    this.error = err.message;
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        openCreateModal() {
            alert("Abrir modal de creación (a implementar)");
        }
    }
}



function materialForm(materialId = null) {
  return {
    form: {
      name: '',
      code: '',
      unit: '',
      group_id: ''
    },
    groups: [],
    loading: false,
    success: false,
    error: '',
    formDisabled: false,
    buttonLabel: materialId ? 'Actualizar' : 'Crear',

    async init() {
        this.loading = false;
      try {
        const resGroups = await fetch('/api/v1/material-groups');
        this.groups = await resGroups.json();
      } catch (e) {
        console.error('Error cargando grupos', e);
      }

      if (materialId) {
        try {
          const res = await fetch(`/api/v1/materials/${materialId}`);
          const data = await res.json();
          this.form = {
            name: data.name,
            code: data.code,
            unit: data.unit,
            group_id: data.group_id || ''
          };
        } catch (e) {
          this.error = 'Error cargando material';
        }
      }
    },

    async submit() {
      this.loading = true;
      this.error = '';
      this.success = false;

      const payload = {
        ...this.form,
        group_id: this.form.group_id === '' ? null : parseInt(this.form.group_id)
      };

      try {
        const res = await fetch(materialId ? `/api/v1/materials/${materialId}` : '/api/v1/materials', {
          method: materialId ? 'PATCH' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || 'Error inesperado');

        this.success = true;

        this.formDisabled = true;
        console.log(data.id)
        setTimeout(() => {
          window.location.href = `/materials/${data.id}`;
        }, 1000);
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.error = err.message;
      }
    }
  }
}


function materialDetail(id) {
  return {
    material: {},
    async init() {
      try {
        const res = await fetch(`/api/v1/materials/${id}`);
        const data = await res.json();
        this.material = data;
        console.log(data)
      } catch (error) {
        console.error("Error cargando material:", error);
      }
    }
  }
}


function lotsList(id) {
  return {
    material_id: id,
    lots: [],
    loading: false,

    init() {
      this.material_id = id;
      console.log('init;;;', this.material_id)
      this.fetchLots();
    },

    async fetchLots() {
      this.loading = true;
      try {
        console.log('in fetch', this.material_id)
        const res = await fetch(`/api/v1/materials/${this.material_id}/lots?quantity__gt=0`);
        const data = await res.json();
        this.lots = data;
        console.log(data)
        console.log(this.lots)
      } catch (err) {
        console.error('Error al cargar los lotes', err);
      }
      this.loading = false;
    }
  };
}


function lotDetail(id) {
  return {
    lot: {},
    loading: false,
    async init() {
      this.loading = true;
      try {
        const res = await fetch(`/api/v1/material-lots/${id}`);
        this.lot = await res.json();
      } catch (err) {
        console.error('Error al cargar el lote', err);
      }
      this.loading = false;
    }
  }
}
