

function statusBadge({
    value = null,                   // estado inicial o usa x-model
    kind  = 'sale_order',           // sale_order | production_order | is_active | ...
    pill  = true,                   // badge redondeado
    size  = 'md',                   // sm | md
    className = '',                 // clases extra
    palette = null                  // opcional: sobreescribe/añade paletas
    } = {}) {

    // Paletas por defecto
    const defaults = {
      sale_order: {
        'Aprobada' : 'bg-success',
        'Pendiente': 'bg-warning text-dark',
        'Rechazada': 'bg-danger',
        'Cancelada': 'bg-secondary'
      },
      production_order: {
        'Borrador'   : 'bg-secondary',
        'En Proceso' : 'bg-primary',
        'Terminado'  : 'bg-success',
        'Cancelado'  : 'bg-danger'
      },
      is_active: {
        'true'  : 'bg-success',
        'false' : 'bg-secondary'
      }
    };

    // merge palettes (shallow)
    const PALETTE = Object.assign({}, defaults, palette || {});

    return {
      value, kind, pill, size, className,

      // calcula clase + texto mostrado
      compute() {
        const map = PALETTE[this.kind] || {};
        const isBoolKind = this.kind === 'is_active';

        // valor normalizado a string para lookup
        const key = isBoolKind ? String(!!this.value) : String(this.value ?? '');

        const cls  = map[key] || 'bg-light text-dark';
        const text = isBoolKind
          ? (this.value ? 'Activo' : 'Inactivo')
          : (this.value ?? '');

        return { cls, text };
      },

      render() {
        const { cls, text } = this.compute();
        const base = 'badge ' + (this.pill ? 'rounded-pill ' : '');
        const padding = this.size === 'sm' ? 'px-2 py-1' : 'px-3';
        // aplica clases y texto directamente al elemento raíz
        this.$el.className = `${base}${padding} ${cls} ${this.className}`.trim();
        this.$el.textContent = text;
      },

      set(v) { this.value = v; },   // por si quieres actualizar manualmente

      init() {
        // pintar inicial
        this.render();

        // re-render ante cambios
        this.$watch('value', () => this.render());
        this.$watch('kind',  () => this.render());

        // Si usas x-modelable, no necesitamos hacer dispatch porque no cambiamos value desde dentro.
      }
    };
  }

  // registro
  document.addEventListener('alpine:init', () => {
    Alpine.data('statusBadge', statusBadge);
  });
