function productWizard({ productId = null, startStep = null } = {}) {
  return {
    // Configuración inicial
    startStep,
    step: startStep || 1,
    productId,
    // Payload central
    productData: {
      code: '',
      name: '',
      line_id: null,
      subline_id: null,
      target_id: null,
      collection_id: null,
      description: '',
      designs: [],
      variants: [],
      materials: [],
    },

    //catalogos y estados
    lines: [],
    sublines: [],
    targets: [],
    collections: [],
    // Flags + combinación de prefijo
    loading: false,
    error:   '',
    code_combination:'',
    availableColors: [],
    selectedColors: [],
    existingDesignCodes: null,
    newDesignCode: null,
    isDuplicateDesign: true,




    init() {
      console.log('init:', this.step)
      console.log('product_id:', this.productId)
      this.fetchLines();
      this.fetchSubLines();
      this.fetchTargets();
      // Si productId existe, cargamos datos base
      if (this.productId) this.loadProductContext();
      // Carga pasos necesarios según startStep
      if (this.step <= 2) {
        this.fetchColors();
      }
      if (this.step <= 3) this.fetchSeries();

    },

    // --- Contexto producto (solo si editing design) ---
    async loadProductContext() {
      try {
        const prod = await (await fetch(`/api/v1/products/${this.productId}`)).json();
        this.productData.code = prod.code;
        // Si startStep>1, precarga diseños existentes...
        this.productData.designs = (await (await fetch(`/api/v1/product-designs?product_id=${this.productId}`)).json())
          .map(d => ({ color_ids: d.colors.id, design_code: d.code }));
        console.log('this product_designs', this.productData.designs)
        this.existingDesignCodes = this.productData.designs.map(d => d.design_code);
        console.log('this existing codes init', this.existingDesignCodes)
      } catch (e) {
        console.error(e);
        this.error = 'Error cargando datos del producto.';
      }
    },

    // --- Pasos comunes ---
    // Paso 1: Datos básicos (solo si startStep<=1)

    async fetchLines() {
      try {
        this.lines = await (await fetch('/api/v1/product-lines')).json();
      } catch (e) { console.error(e); }
    },

    async fetchSubLines() {
      try {
        this.sublines = await (await fetch('/api/v1/product-sublines')).json();
      } catch (e) { console.error(e); }
    },

    async fetchTargets() {
      try {
        this.targets = await (await fetch('/api/v1/product-targets')).json();
      } catch (e) { console.error(e); }
    },

    // Filtra colecciones cada vez que cambia línea/sub-línea/target
    async fetchCollections() {
      const params = new URLSearchParams();
      if (this.productData.line_id)   params.append('line_id',   this.productData.line_id);
      if (this.productData.subline_id) params.append('subline_id', this.productData.subline_id);
      if (this.productData.target_id) params.append('target_id', this.productData.target_id);
      this.productData.code='';
      this.loading = true;
      console.log('init collections')
      if(this.productData.line_id && this.productData.target_id){
        try {
                const res = await fetch(`/api/v1/product-collections/specific?${params}`);
                this.collections = await res.json();
                if(this.collections === null || this.collections.length==0){
                  alert('No hay colecciones para esta linea. Cree una coleccion')
                }
                console.log('fetched collections')
              } catch (e) {
                console.error(e);
                this.error = 'No pudimos cargar colecciones.';
              } finally {
                this.loading = false;
              }
      }else{
        console.info('Debe escoger una linea y un target')
      }
    },

    // Genera el código completo (prefijo + auto-incremental)
    async fetchNextCode() {
      const params = new URLSearchParams();
      if (this.productData.line_id)   params.append('line_id',   this.productData.line_id);
      if (this.productData.subline_id) params.append('subline_id', this.productData.subline_id);
      if (this.productData.target_id) params.append('target_id', this.productData.target_id);
      if (this.productData.collection_id) params.append('collection_id', this.productData.collection_id);


      // Solo si hay prefijo válido
      if (!this.productData.line_id, !this.productData.target_id, !this.productData.collection_id) return console.info('seleccione params');
      try {
        const res  = await fetch(`/api/v1/products/next-code?${params}`);
        const data = await res.json();
        this.productData.code = data || '';
      } catch {
        this.error = 'Error al generar código.';
      }
    },


  //--------------------------------------------
  //-------------------------Step2---------------
    async fetchColors(){
      try{
        const resColors = await fetch('/api/v1/colors');
        const dataColors = await resColors.json();
        this.availableColors = dataColors;
      }catch(err){
        console.error('error:', err)
      }
    },

    toggleColor(color) {
      if (this.isColorSelected(color.id)) {
        this.removeColor(color);
      } else {
        this.selectedColors.push(color);
      }
      this.updateDesign();
    },

    isColorSelected(id) {
      return this.selectedColors.some(c => c.id === id);
    },

    removeColor(color) {
      this.selectedColors = this.selectedColors.filter(c => c.id !== color.id);
      this.updateDesign();
    },

    getDesignSuffix() {
      return this.selectedColors.map(c => c.code).join('');
    },

    updateDesign() {
      this.productData.designs = []; // en este modelo, solo un diseño
      if (this.selectedColors.length > 0) {
        const suffix = this.selectedColors.map(c => c.code).join('');
          // 2.b) Nuevo código completo
        this.newDesignCode = this.productData.code + suffix;
        this.error = '';
        this.isDuplicateDesign = false;
          // 2.c) Validación de duplicado
        if(this.existingDesignCodes){
          if (this.existingDesignCodes.includes(this.newDesignCode)) {
            this.error = `El diseño "${this.newDesignCode}" ya existe.`;
            this.isDuplicateDesign = true;
          }
        }



        this.productData.designs.push({
          color_ids: this.selectedColors.map(c => c.id),
          color_codes: this.selectedColors.map(c => c.code),
          color_names: this.selectedColors.map(c => c.name),
          design_code: this.productData.code + this.getDesignSuffix(),
        });
      }
    } ,

//--------------------------------------------------------------
//--------------------------------Step3-----------------------------

    sizeSeries: [],
    selectedSeriesId: '',
    selectedSerie:'',
    sizes: [],
    variants: [],


    async fetchSeries(){
      try{
        const resSeries = await fetch('/api/v1/series');
        const dataSeries = await resSeries.json();
        this.sizeSeries = dataSeries;

      }catch(err){
        console.error('error: ', err)
      }
    },

    async loadSizes() {
      if (!this.selectedSeriesId) {
        this.sizes = [];
        this.variants = [];
        this.productData.variants = [];
        return;
      }

      const res = await fetch(`/api/v1/series/${this.selectedSeriesId}/sizes`);
      const data = await res.json();
      this.sizes = data;
      console.log('sosiz', data)
      this.generateVariants();
      this.fecthSerie();
    },

    async fecthSerie(){
      try{
        const resSerie = await fetch(`/api/v1/series/${this.selectedSeriesId}`);
        const dataSerie = await resSerie.json();
        this.selectedSerie = dataSerie;

      }catch(err){
        console.error('error: ', err);
      }
    },

    removeSerie() {
      this.selectedSeriesId = '';
      this.productData.variants='';
      this.variants = [];
      this.selectedSerie = '';
    },

    generateVariants() {
      if (!this.productData.designs.length || !this.sizes.length) return console.error('No mismo');
      this.productData.variants = [] // solo una serie permitida
      const design = this.productData.designs[0]; // solo uno permitido
      console.log('fessddi', design)
      const prefix = design.design_code;
      this.variants = [];
      this.variants = this.sizes.map(size => ({
        size_id: size.id,
        size_name: size.value,
        variant_code: `${prefix}${size.value}`,
      }));
      this.productData.variants.push({series_ids:[this.selectedSeriesId]})
    },

//------------------------------STEP4--------------------------------
//--------------------------------------------------------------------------
    materialQuery: '',
    materialResults: [],

    async searchMaterials() {
      if (this.materialQuery.length < 2) {
        this.materialResults = [];
        return;
      }

      const res = await fetch(`/api/v1/materials/search?q=${this.materialQuery}`);
      const data = await res.json();
      this.materialResults = data;
    },

    clearSearch() {
      this.materialQuery = '';
      this.materialResults = [];
    },

    addMaterial(mat) {
      if (this.productData.materials.some(m => m.id === mat.id)) return;
        this.productData.materials.push({
          id: mat.id,
          code: mat.code,
          name: mat.name,
          quantity: 0,
          unit: mat.unit
        });
        this.clearSearch();
    },

    removeMaterial(id) {
      this.productData.materials = this.productData.materials.filter(m => m.id !== id);
    },



//-----------------------general wizard----------------------------
//----------------------------------------------------------------

    isStep1Valid() {
      return this.productData.code && this.productData.name ;
    },

    isStep2Valid() {
      return !this.isDuplicateDesign && this.selectedColors.length>0;
    },




    nextStep() {
      if (this.step < 4) this.step++;
      console.log('step', this.step)
    },

    prevStep() {
      if (this.step > 1 && this.step > startStep) this.step--;

    },

    resetWizard() {
      if (confirm('¿Cancelar creación del producto?')) {
        window.location.href = '/products';
      }
    },

    async submitFinal() {
      try {

        //--------------------------------------------
        //------------------Diseno-------------------
        if (this.productId && this.startStep===2) {
        /* crear disenoy obtener productId */
          this.productData.product_id = this.productId;
          const res = await fetch('/api/v1/product-designs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.productData),
          });
          const data = await res.json();
          if (res.ok) {
            alert('✅ Diseno creado correctamente');
            window.location.href = `/products/designs/${data.id}`;
          } else {
            alert(data.message || '❌ Error al crear Diseno');
          }


        }else{
           /* crear producto y obtener productId */
           const res = await fetch('/api/v1/products', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.productData),
          });
          const data = await res.json();
          if (res.ok) {
            alert('✅ Producto creado correctamente');
            window.location.href = `/products/${data.id}`;
          } else {
            alert(data.message || '❌ Error al crear producto');
          }
        }



      } catch (e) {
        alert('❌ Error de conexión');
      }
    }
  };
}
