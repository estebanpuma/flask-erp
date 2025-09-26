;(function(window) {

  const showToast=(msg,type='info',delay=3000)=>{
    const t=document.createElement('div')
    t.className=`toast align-items-center text-bg-${type} border-0`
    t.role='alert'
    t.innerHTML=`<div class="d-flex">
       <div class="toast-body">${msg}</div>
       <button class="btn-close btn-close-white me-2 m-auto"
               data-bs-dismiss="toast"></button></div>`
    document.body.appendChild(t)
    const bs=bootstrap.Toast.getOrCreateInstance(t,{delay})
    bs.show(); t.addEventListener('hidden.bs.toast',()=>t.remove())
  }






  /* ───── BADGE DINÁMICO ───── */
  function statusBadge(value, kind = 'sale_order') {
    const palette = {
      sale_order: {
        Aprobada : 'bg-success',
        Pendiente: 'bg-warning text-dark',
        Rechazada: 'bg-danger',
        Cancelada: 'bg-secondary'
      },
      production_order: {
        Borrador   : 'bg-secondary',
        'En Proceso' : 'bg-primary',
        Terminado  : 'bg-success',
        Cancelado  : 'bg-danger'
      },
      is_active:{
        true    : 'bg-success',
        false   : 'bg-secondary'
      }
    };
    const cls = (palette[kind] || {})[value] || 'bg-light text-dark';
    const text = kind==='is_active'?value==true?'Activo':"Inactivo":value
    return /*html*/`
      <span x-data
            :class="'badge rounded-pill px-3 ${cls}'"
            x-text="'${text}'">
      </span>`;
  }

/* ─── BOTÓN DE ACCIÓN v2 ───
*  • variantes Bootstrap (`primary`, `success`, …)
*  • tamaño `sm | md`
*  • icono opcional (Bootstrap Icons o texto)
*  • estado `loading`, `disabled`
*  • aria-label automático                 */
function actionBtn ({
    label   = 'Acción',
    href    = null,          // si hay href → <a>, si no → <button>
    variant = 'dark',
    size    = 'sm',          // 'lg' o 'md'
    icon    = '',            // 'plus', 'trash', …
    disabled = false,
    loading  = false,
    w     = 'w-100',
    tooltip  = ''            // texto tooltip (opcional)
    } = {}) {

    const fw       = 'semibold'
    const height    = "height: 48px"
    const tag      = href ? 'a' : 'button'
    const spacing  = icon && label ? 'me-1' : ''
    const isLoading= loading ? 'disabled' : ''
    const attrDis  = disabled ? 'disabled' : ''
    const dataBs   = tooltip ? `data-bs-toggle="tooltip" title="${tooltip}"` : ''
    const iconHtml = icon
        ? `<i class="bi bi-${icon} ${spacing}"></i>`
        : ''

    const content  = loading
        ? `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span class="visually-hidden">Cargando…</span>`
        : `${iconHtml}${label}`

    return /*html*/`
        <${tag}
        ${href ? `href="${href}"` : 'type="button"'}
        class="btn btn-${variant} rounded-pill fw-${fw} ${w} ${size==='sm'?'btn-sm':'btn-md'} "
        ${attrDis} ${isLoading} ${dataBs}
        aria-label="${label}"
        style="${height}">
        ${content}
        </${tag}>` ;
    }

    /* ─── BOTÓN “CREAR” ───
    *  • Ícono “plus-circle”
    *  • Oculta texto en pantallas < md
    *  • Variante, posición flotante y tamaño opcionales     */
    function createBtn ({
        href    = '#',
        label   = 'Crear',
        size    = 'md',          // 'sm' | 'md'
        variant = 'dark',
        float   = false          // true → fixed bottom-end
        } = {}) {

        const classes = [
            `btn btn-${variant}`,
            size === 'sm' ? 'btn-sm' : '',
            'd-flex align-items-center gap-1'
        ]
        if (float) classes.push('position-fixed bottom-0 end-0 m-3 shadow-lg rounded-circle')

        return /*html*/`
            <a href="${href}"
            class="${classes.join(' ').trim()}"
            aria-label="${label}">
            <i class="bi bi-plus-circle"></i>
            <span class="d-none d-md-inline">${label}</span>
            </a>`;
        }






  function floatingInputSelect(
    {
      label = 'Input',
      id    = 'InputSelect',
      model = 'model',
      list  = 'list',
      show  = 'name',
      change  = '',
      input   = '',
      click   = '',
      blur    = '',
      required = true

    }){

      return /*html*/`
        <div class="form-floating mb-3">
            <select class="form-select form-select-lg ps-4 px-1 rounded-5 fw-semibold fs-6" x-model="${model}"
            @change="${change}" @click="${click}" style="height: 72px;" id="${id}" ${required==true?'required':''}>
              <option value="" class='text-muted user-select-none'>Seleccione</option>
              <template x-for="el in ${list}" :key="el.id">
                <option :value="el.id" x-text="el.${show}"></option>
              </template>
            </select>
            <label for="${id}" class="ps-4 text-muted small">${label}</label>
        </div>
      `
  }



  /* Exponemos todas las funciones en un namespace global */
  window.guifer = window.guifer || {}
  window.guifer.components = {
    alert:  {showToast, alert},
    btn:    {actionBtn, createBtn,},
    input:  {floatingInputSelect,},
    status: {statusBadge,},
  };

})(window);
