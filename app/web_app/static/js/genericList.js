// static/js/genericList.js
window.genericList = function(apiUrl,baseHref, columns) {
  return {
    apiUrl,
    columns,            // [ { field, label, filterable }, … ]
    items: [],          // datos traídos
    filteredItems: [],  // datos tras filtro
    filters: {},        // { field1: '', field2: '', … }
    globalFilter: '',   
    baseHref,    // prefijo para los enlaces, e.g. '/products/collections'
    loading: true,   // ← cargando al inicio
    error: '',       // ← mensaje de error

    init() {
      this.fetchItems();
      this.columns.forEach(c => {
        if (c.filterable) this.filters[c.field] = '';
      });
    },

    // Helper para leer rutas anidadas safely
    getNested(obj, path) {
      return path.split('.').reduce((o, key) => (o != null ? o[key] : undefined), obj);
    },

    async fetchItems() {
      this.loading = true;
      this.error = '';
      try {
        const res = await fetch(this.apiUrl);
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();
        // 1) Base items
        const raw = Array.isArray(data) ? data : data.items || [];
        // 2) Aplana los campos anidados según columns
        this.items = raw.map(item => {
          // genera href si aplica
          const href = this.baseHref ? `${this.baseHref}/${item.id}` : null;
          // construye mapa de valores planos
          const flat = {};
          this.columns.forEach(c => {
            // valor anidado o directo
            flat[c.field] = this.getNested(item, c.field);
          });
          return { ...item, ...flat, href };
        });
        this.filteredItems = this.items;
      } catch (e) {
        console.error('Error cargando datos:', e);
        this.error = 'No se pudo conectar con el servidor.';
      } finally {
        this.loading = false;
      }
    },

    filterItems() {
      const gf = this.globalFilter.toLowerCase();
      this.filteredItems = this.items.filter(item => {
        // 1️⃣ globalFilter: busca en **todos** los valores del objeto
        const matchesGlobal = !gf || Object.values(item)
          .some(v => String(v).toLowerCase().includes(gf));

        // 2️⃣ filtros por columna
        const matchesCols = this.columns.every(c => {
          if (!c.filterable) return true;
          const q = this.filters[c.field].toLowerCase();
          return !q || String(item[c.field] || '')
            .toLowerCase().includes(q);
        });

        return matchesGlobal && matchesCols;
      });
    },
  }
}
