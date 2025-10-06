// static/js/genericList.js
function genericList(apiUrl,baseHref, columns) {
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
      console.log('initLis')
      this.fetchItems();
      this.columns.forEach(c => {
        if (c.filterable) this.filters[c.field] = '';
      });
    },

    /* ───────── helpers ───────── */
    deepValue(obj, path) {
      return path.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
    },

    cellHtml (row, col) {

        const raw = this.deepValue(row, col.field)

        /* ① Mini-componente global (badge, botón, etc.) */
        if (typeof col.component === 'string') {
          const comp = window.guifer?.components?.status?.[col.component]
          if (comp) {
            const kind = col.props?.kind ?? 'default'
            return comp(raw, kind)
          }
        }

        /* ② Función pasada directamente en columns */
        if (typeof col.component === 'function') {

          return col.component(raw, col.props || {})

        }

        /* ③ Formatter específico */
        if (col.formatter) return col.formatter(raw)

        /* ④ Valor por defecto */
        return raw ?? '—'

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
          //const flat = {};
          //this.columns.forEach(c => {
            // valor anidado o directo
          //  flat[c.field] = this.deepValue(item, c.field);
          //});
          return { ...item,  href };
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
