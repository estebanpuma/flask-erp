// static/js/genericDetail.js
window.genericDetail = function(apiUrl, fields, icon) {
  return {
    apiUrl,
    fields,      // Array de { field, label, isList?, itemText? }
    item: {},    // Aquí irá el objeto “aplanado”
    loading: true,
    error: '',
    icon,

    init() {
      this.fetchItem();
    },

    // Helper para leer rutas anidadas
    getNested(obj, path) {
      return path.split('.').reduce((o, key) =>
        (o != null ? o[key] : undefined), obj);
    },

    async fetchItem() {
      this.loading = true;
      this.error = '';
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
      } catch (e) {
        console.error('Error cargando detalle:', e);
        this.error = 'No se pudo cargar los datos.';
      } finally {
        this.loading = false;
      }
    }
  }
}
