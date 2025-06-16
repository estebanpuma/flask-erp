function productWizard() {
  return {
    step: 1,
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

    init() {
      console.log('init:', this.step)
      this.fetchLines();
      this.fetchSubLines();
      this.fetchTargets();
      this.fetchColors();
      this.fecthSeries();

    },

    //------------------------------------
    //------------Step1-----------------
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


    async fecthSeries(){
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
      if (!this.productData.designs.length || !this.sizes.length) return;

      const design = this.productData.designs[0]; // solo uno permitido
      const prefix = design.design_code;

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


    nextStep() {
      if (this.step < 4) this.step++;
      console.log('step', this.step)
    },

    prevStep() {
      if (this.step > 1) this.step--;
    },

    resetWizard() {
      if (confirm('¿Cancelar creación del producto?')) {
        window.location.href = '/products';
      }
    },

    async submitFinal() {
      try {
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
      } catch (e) {
        alert('❌ Error de conexión');
      }
    }
  };
}
