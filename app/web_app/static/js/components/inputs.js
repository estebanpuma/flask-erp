    function inputText({
        id          = null,
        label       = 'Nombre',
        placeholder = 'Escribe algo..',
        initial     = '',
        type        = 'text',          // text | email | number | etc.
        name        = '',
        is_invalid  = false,
        required    = false,
        disabled    = false,
        readonly    = false,
        autocomplete= 'off',
        maxLength   = null,            // número o null
        pattern     = null,            // RegExp en string, p.ej. "^[A-Za-z ]+$"
        help        = '',              // texto de ayuda opcional
        invalidText = '',
        showInvalid = false,           // ← permite pasar "tried" del padre
        trim        = true,            // aplicar .trim en el input
        debounce    = 0,               // ms (0 = sin debounce)
        inputClass  = ''               // clases extra para <input>
    } = {}) {
        return {
            // estado público (puerto x-modelable)
            value: initial ?? '',
            // props reactivas para la plantilla
            id: id || `in_${Math.random().toString(36).slice(2,9)}`,
            label, placeholder:placeholder, type, name,
            required, disabled, readonly, autocomplete, maxLength, pattern,
            help, invalidText:invalidText, showInvalid, trim, debounce, inputClass, 
            is_invalid: is_invalid,

            // regla de invalidez básica + patrón
            get invalid() {
                if (this.is_invalid) return true
                if (this.required && (!this.value || String(this.value).trim() === '')) return true;
                if (this.pattern) {
                try {
                    const re = new RegExp(this.pattern);
                    if (this.value && !re.test(this.value)) return true;
                } catch(_) { /* patrón inválido: ignorar */ }
                }
                if (typeof this.maxLength === 'number' && (this.value?.length || 0) > this.maxLength) return true;
                return false;
            },

            init() {
                // 1) Plantilla una sola vez
                this.$el.innerHTML = /*html*/`
                <div class="form-floating mb-3">
                    <input
                    class="form-control ${this.inputClass}"
                    :class="invalid?'is-invalid':''"
                    :id="id"
                    :name="name"
                    :type="type"
                    placeholder='Escribe'
                    :disabled="disabled"
                    :readonly="readonly"
                    :autocomplete="autocomplete"
                    :maxlength="maxLength || null"
                    :pattern="pattern || null"
                    :required="required"
                    ${this.trim ? 'x-model.trim="value"' : 'x-model="value"'}
                    ${this.debounce ? `@input.debounce.${this.debounce}ms="onInput"` : '@input="onInput"'}
                    @blur="touched = true"
                    >
                    <label :for="id" class='text-muted' x-text="label"></label>
                    <div class="invalid-feedback" x-text="invalidText"></div>
                    <small x-show="help" class="text-muted d-block mt-1" x-text="help"></small>
                </div>
                
                `;

                // 2) Sembrar desde el x-model del padre si existe
                const m = this.$el._x_model;
                if (m) {
                const current = m.get();
                if (typeof current !== 'undefined') this.value = current;
                else m.set(this.value);
                }

                // 3) Sincronía con el padre
                this.$watch('value', v => this.$dispatch('input', v));
            },

            onInput() {
                // lugar para normalizaciones adicionales si quieres
            }
        };
    }

    // registro global + alias corto
    window.guifer = window.guifer || {};
    guifer.components = guifer.components || {};
    guifer.components.input = guifer.components.input || {};
    guifer.components.input.inputText = inputText;

    document.addEventListener('alpine:init', () => {
        Alpine.data('inputText', inputText);
    });




function boolSwitch({
    id        = null,
    initial   = false,
    label     = 'Estado',
    help      = '',             // texto de ayuda opcional bajo el switch
    name      = '',             // name para submit nativo (opcional)
    disabled  = false,
    required  = false,
    showState = false,          // mostrar “Activo/Inactivo” junto a la etiqueta
    onText    = 'Activo',
    offText   = 'Inactivo',
    sizeClass = 'lg'              // puedes pasar 'form-switch-lg' si tienes esa clase
  } = {}) {
    return {
      // puerto público (x-modelable)
      value: !!initial,

      // opciones en el estado
      id: id || `sw_${Math.random().toString(36).slice(2, 9)}`,
      label, help, name, disabled, required, showState, onText, offText, sizeClass,

      init() {
        // 1) pintar plantilla UNA sola vez
        this.$el.innerHTML = /*html*/`
          <div class="form-check form-switch form-check-reverse form-control-${this.sizeClass}">
            <label class="form-check-label" :for="id">
              <span x-text="label"></span>
              <template x-if="showState">
                <span class="ms-1" x-text="value ? '${onText}' : '${offText}'"></span>
              </template>
            </label>
            <input  class="form-check-input"
                    type="checkbox"
                    role="switch"
                    :id="id"
                    x-model="value"
                    :disabled="disabled"
                    :required="required"
                    ${name ? `name="${name}"` : ''}>
          </div>
          <small x-show="help" class="text-muted d-block" x-text="help"></small>
        `;

        // 2) sincronizar con el padre (x-model)
        //    si el padre ya tiene valor, úsalo; si no, siembra el inicial
        const m = this.$el._x_model;
        if (m) {
          const current = m.get();
          if (typeof current !== 'undefined') this.value = !!current;
          else m.set(this.value);
        }
        this.$watch('value', v => this.$dispatch('input', v));
      },

      toggle() { this.value = !this.value; }
    };
  }



  document.addEventListener('alpine:init', () => {
    Alpine.data('boolSwitch', boolSwitch); // atajo: x-data="boolSwitch({...})"
  });

    // Componente Alpine para inputQtyState
/* ----------  estado + lógica  ---------- */
function inputQtyState ({ initial = 0, step = 1, min = 0, max = null, size = 'lg', id = 'qty', required = true } = {}) 
    {
        const clamp = v => Math.max(min, max !== null ? Math.min(max, v) : v);

        return {
        /* puerto público de x-modelable */
        value: clamp(initial),

        /* primera vez que Alpine arranca este scope */
        init () {
            /* pinta la plantilla SOLO una vez  */
            this.$el.innerHTML = /*html*/`
            <button type="button"
                    class="btn btn-outline-dark btn-${size} me-1"
                    :class="value<=${min} ? 'opacity-50 pointer-events-none' : ''"
                    @click="dec">−</button>

            <input  id="${id}" type="text" pattern="[0-9.]*" inputmode="decimal"
                    class="form-control form-control-${size} fw-semibold text-center px-1"
                    style="max-width:60px;min-width:30px;"
                    x-model="value" @input="sanitize"
                    ${required ? 'required' : ''} >

            <button type="button"
                    class="btn btn-outline-dark btn-${size} ms-1"
                    ${max !== null
                        ? `:class="value>=${max} ? 'opacity-50 pointer-events-none' : ''"`
                        : ''}
                    @click="inc">+</button>
            `;

            /* propaga cambios al padre (x-model) */
            this.$watch('value', v => this.$dispatch('input', v));
        },

        /* acciones */
        inc () { this.value = clamp(this.value + step); },
        dec () { this.value = clamp(this.value - step); },
        sanitize(e) {
            const raw = e.target.value;

            /* 1 ▸ Elegir la expresión según si step tiene decimales */
            const onlyDigits        = /[^0-9]/g;        // 12345
            const digitsPlusDot     = /[^0-9.]/g;       // 12.34
            const needsDot          = step % 1 !== 0;   // true si step = 0.1, 0.01…

            /* 2 ▸ Filtrar caracteres no permitidos */
            let clean = raw.replace(needsDot ? digitsPlusDot : onlyDigits, '');

            /* 3 ▸ Si admite punto, mantener uno solo y recortar decimales */
            if (needsDot) {
            // quitar puntos extra
            clean = clean.replace(/\.(?=.*\.)/g, '');
            // limitar nº de decimales según step
            const decPlaces = (step.toString().split('.')[1] || '').length;
            if (clean.includes('.')) {
                const [int, dec] = clean.split('.');
                clean = int + '.' + dec.slice(0, decPlaces);
            }
            }

            /* 4 ▸ Convertir a número y clampearlos a min/max */
            const num = clean === '' ? NaN : Number(clean);
            if (!isNaN(num)) {
            this.value = clamp(num);          // clamp es tu helper min-max
            } else if (clean === '') {
            this.value = '';                  // permitir borrar todo
            }
        }
        };
    };
  
    document.addEventListener('alpine:init', () => {
    Alpine.data('inputQty', inputQtyState);
    });


function inputTextArea({
    id          = null,
    label       = 'Descripción',
    placeholder = 'Escribe aquí…',
    initial     = '',
    rows        = 3,
    maxLength   = 200,
    required    = false,
    disabled    = false,
    readonly    = false,
    autocomplete= 'off',
    help        = '',                  // texto de ayuda (opcional)
    invalidText = 'Este campo es obligatorio.',
    showCount   = true,                // mostrar contador
    trim        = true,                // aplicar .trim
    debounce    = 150,                 // ms
    inputClass  = ''                   // clases extra para el <textarea>
  } = {}) {

    return {
      // puerto público (x-modelable)
      value: initial ?? '',
      // props
      id: id || `ta_${Math.random().toString(36).slice(2,9)}`,
      label, placeholder, rows, maxLength, required, disabled, readonly,
      autocomplete, help, invalidText, showCount, trim, debounce, inputClass,
      touched: false,
      count: (initial ?? '').length,

      get invalid () {
        if (this.required && String(this.value).trim() === '') return true;
        if (typeof this.maxLength === 'number' && (this.value?.length || 0) > this.maxLength) return true;
        return false;
      },

      init () {
        // plantilla (una sola vez)
        this.$el.innerHTML = `
          <div>
            <label class="form-label" :for="id" x-text="label"></label>
            <textarea
              class="form-control ${this.inputClass}"
              :class="{'is-invalid': (touched) && invalid}"
              :id="id"
              :rows="rows"
              :maxlength="maxLength || null"
              :placeholder="placeholder"
              :disabled="disabled"
              :readonly="readonly"
              :autocomplete="autocomplete"
              ${this.trim ? 'x-model.trim="value"' : 'x-model="value"'}
              @input.debounce.${this.debounce}ms="onInput"
              @blur="touched = true"
            ></textarea>
            <div class="invalid-feedback" x-text="invalidText"></div>
            <div class="form-text text-end" x-show="showCount" x-text="count + '/' + (maxLength || 0)"></div>
            <small x-show="help" class="text-muted d-block mt-1" x-text="help"></small>
          </div>
        `;

        // si el padre ya tiene valor vía x-model, usarlo; si no, sembrar initial
        const m = this.$el._x_model;
        if (m) {
          const current = m.get();
          if (typeof current !== 'undefined') this.value = current;
          else m.set(this.value);
        }

        // sincronía + contador
        this.$watch('value', v => {
          this.count = (v?.length || 0);
          this.$dispatch('input', v);
        });
      },

      onInput () { /* punto único de normalización si necesitas algo extra */ }
    };
  }

  // registro
  document.addEventListener('alpine:init', () => {
    Alpine.data('inputTextArea', inputTextArea);

  });

function floatingInputSelect(
    {
      label     = 'Input',
      id        = 'InputSelect',
      initial   = '',
      list      = 'list',
      show      = 'name',
      change    = '',
      input     = '',
      click     = '',
      blur      = '',
      required  = true,
      size      = 'md',
      help        = '',                  // texto de ayuda (opcional)
    }={}){
      
    return{
        value: initial,
        help,
        init(){
            this.$el.innerHTML =`
            <div class="form-floating mb-3">
                <select class="form-select form-select-${size}" x-model="value" placeholder="placeholder"
                @change="${change}" @click="${click}" id="${id}" ${required==true?'required':''}>
                <option value="" class='text-muted user-select-none'>Seleccione</option>
                <template x-for="el in ${list}" :key="el.id">
                    <option :value="el.id" x-text="el.${show}"></option>
                </template>
                </select>
                <label for="${id}" >${label}</label>
                <small x-show="help" class="text-muted d-block mt-1" x-text="help"></small>
            </div>
        `;
        //const m = this.$el._x_model;
        },
      }


  }
  // registro
  document.addEventListener('alpine:init', () => {
    Alpine.data('inputSelect', floatingInputSelect);

  });
