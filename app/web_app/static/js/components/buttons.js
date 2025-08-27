; (function(){

  function actionBtn({
    label    = 'Acción',
    href     = null,          // si hay href → <a>, si no → <button>
    variant  = 'dark',
    size     = 'md',          // 'sm' | 'md' | 'lg'
    icon     = null,            // 'plus', 'trash', …
    disabled = false,
    loading  = false,
    width    = 'w-100',       // clases de ancho (p.ej. 'w-100', 'w-auto')
    tooltip  = '',            // texto tooltip (opcional)
    pill     = false           // borde redondeado estilo "pill"
  } = {}) {
    return {
      // estado
      label, href, variant, size, icon, disabled, loading, width, tooltip, pill,

      get btnClasses () {
        const sz  = this.size === 'sm' ? 'btn-sm' : (this.size === 'lg' ? 'btn-lg' : '');
        const pill= this.pill ? 'rounded-pill' : '';
        return `btn btn-${this.variant} ${sz} ${pill} fw-semibold ${this.width}`;
      },

      init () {
        // plantilla una sola vez
        this.$el.innerHTML = `
          ${this.href ? `
            <a  :href="disabled || loading ? 'javascript:void(0)' : '${this.href}'"
                class="${this.btnClasses}"
                :class="{ 'disabled': disabled || loading }"
                ${this.tooltip ? `data-bs-toggle="tooltip" title="${this.tooltip}"` : ''}
                @click="onClick">
              <template x-if="loading">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              </template>
              <template x-if="!loading">
                <span>
                  <template x-if="icon"><i :class="'bi bi-' + icon" class="me-1"></i></template>
                  <span class="small">${label}</span>
                </span>
              </template>
            </a>
          ` : `
            <button type="button"
                    :disabled="disabled || loading"
                    class="${this.btnClasses}"
                    ${this.tooltip ? `data-bs-toggle="tooltip" title="${this.tooltip}"` : ''}
                    @click="onClick">
              <template x-if="loading">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              </template>
              
                <span>
                  <template x-if="icon"><i :class="'bi bi-' + icon" class="me-1"></i></template>
                  <span class="small">${label}</span>
                </span>
              
            </button>
          `}
        `;

        // si usas tooltips de Bootstrap, activarlos (opcional)
        if (this.tooltip && window.bootstrap?.Tooltip) {
          this.$nextTick(() => new bootstrap.Tooltip(this.$el.querySelector('[data-bs-toggle="tooltip"]')));
        }
      },

      onClick (e) {
        if (this.disabled || this.loading) {
          e.preventDefault(); e.stopPropagation(); return;
        }
        // notifica al padre y deja pasar el click (para <a>, navega)
        this.$dispatch('action');
      },

      // métodos utilitarios
      setLoading(v){ this.loading = !!v; },
      setDisabled(v){ this.disabled = !!v; }
    };
  }



  document.addEventListener('alpine:init', () => {
    Alpine.data('actionBtn', actionBtn);

      });



})()