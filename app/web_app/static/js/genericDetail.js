// static/js/genericDetail.js
window.genericDetail = function(apiUrl, fields, icon, backrefURL, editURL) {
  return {
    apiUrl,
    backrefURL,
    fields,      // Array de { field, label, isList?, itemText? }
    item: {},    // Aquí irá el objeto “aplanado”
    loading: true,
    error: '',
    editURL,
    icon,

    init() {
      console.log('init detail')
      this.fetchItem();
    },

    // Helper para leer rutas anidadas
    getNested(obj, path) {
      return path.split('.').reduce((o, key) =>
        (o != null ? o[key] : undefined), obj);
    },

    async loadGallery() {
      try {
        let res = await fetch(`/api/v1/media/designs/${this.item.id}`)
        console.info('load gallery: ', res)
        if (!res.ok) throw new Error(`Error ${res.status}`)
        const gallery1 = await res.json()
        if(gallery1 !== undefined && gallery1 !== null && gallery1[0]){
          let res2 = await fetch(`/api/v1/media/img/designs/${gallery1[0].filename}`)
          console.info('load img: ', res2)
          if (!res2.ok) throw new Error(`Error 2222 ${res2.status}`)
            this.item.image = res2.url
        }   
      } catch (e) {
        this.error = `No se pudo cargar la galería:${e.toString()} `
        console.log(e)
      }
    },

    async fetchItem() {
      this.loading = true;
      this.error = '';
      console.log('error: ', this.error)
      try {
        const res  = await fetch(this.apiUrl);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        // 1) Aplanar campos simples y listas ← aquí está la novedad
        const flat = {};
        this.fields.forEach(f => {
          if (f.isList) {
            // Obtenemos el array original (o [])
            const arr = this.getNested(data, f.field) || [];
            // Si tienen itemText (función), lo aplicamos; sino dejamos el valor tal cual
            flat[f.field] = f.itemText
              ? arr.map(elem => f.itemText(elem))
              : arr;
          } else {
            flat[f.field] = this.getNested(data, f.field);
          }
        });

        // 2) Fusionamos
        this.item = { ...data, ...flat };
        console.info('item', this.item)
        this.loadGallery()
      } catch (e) {
        console.error('Error cargando detalle:', e);
        this.error = 'No se pudo cargar los datos.';
      } finally {
        this.loading = false;
      }
    },

    async editObj(){
      if(this.editURL) window.location.href = this.editURL; 
    },

    async deleteObj(){
      try{

      const res = await fetch(this.apiUrl, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await res.json();
        this.success = res.ok;
        this.message = this.success ? '✅ Borrado' : (data.message || '❌ Error al borrar');
        if (this.success) {
          alert(this.message)
          if(this.backrefURL)
            window.location.href = this.backrefURL; 
        }
        window.location.href = history.back();

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
