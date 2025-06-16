// static/js/genericDetail.js
window.genericDetail = function(apiUrl, fields, icon) {
  return {
    apiUrl,       // URL de la API para fetch
    fields,       // ['code': code,'name':name,'line_name':line.name,'size.value',…]
    item: {},     // objeto a usar en el template
    loading: true,
    error: '',
    icon,
    
    init() {
      this.fetchItem();
    },

    // helper para leer rutas anidadas
    getNested(obj, path) {
      return path.split('.').reduce((o, key) => (o != null ? o[key] : undefined), obj);
    },

    async fetchItem() {
      this.loading = true;
      this.error = '';
      try {
        const res  = await fetch(this.apiUrl);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        // aplanamos según fields
        const flat = {};
        this.fields.forEach(f => {
          flat[f.field] = this.getNested(data, f.field);
        });
        this.item    = { ...data, ...flat };
      } catch (e) {
        console.error('Error cargando detalle:', e);
        this.error = 'No se pudo cargar los datos.';
      } finally {
        this.loading = false;
      }
    }
  }
}
