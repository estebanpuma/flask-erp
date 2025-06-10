function productWizard() {
  return {
    step: 1,
    productData: {
      code: '',
      name: '',
      line_id: null,
      subline_id: null,
      description: '',
      designs: [],
      variants: [],
      materials: [],
    },

    lines: [],
    sublines: [],
    product_code_letter:'',


    availableColors: [],
    selectedColors: [],

    init() {
      this.fetchLines()
      this.fetchSubLines()
      this.fetchColors()
      this.fecthSeries()
    },

    //------------------------------------
    //------------Step1-----------------
    async fetchLines(){
      try{
        const res = await fetch('/api/v1/product-lines');
        const data = await res.json();
        this.lines = data;
      }catch(err){
        console.error('Error: ',err)
      }
    },

    async fetchSubLines(){
      try{
        const res = await fetch('/api/v1/product-sublines');
        const data = await res.json();
        this.sublines = data;
      }catch(err){
        console.error('Error: ',err)
      }
    },

    fetchNextCode() {
      const letter = this.product_code_letter?.toUpperCase();
      this.product_code_letter = letter;

      if (!letter || !/^[A-Z]$/.test(letter)) {
        this.productData.code = '';
        return;
      }

      fetch(`/api/v1/products/next-code?letter=${letter}`)
        .then(res => res.json())
        .then(data => {
          console.log(data)
          if (data) {
            this.productData.code = data;
          } else {
            this.error = data.message || 'No se pudo generar el código.';
            this.productData.code = '';
          }
        })
        .catch(() => {
          this.error = 'Error al verificar el código.';
          this.productData.code = '';
        });
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
    sizes: [],


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
        this.productData.variants = [];
        return;
      }

      const res = await fetch(`/api/v1/series/${this.selectedSeriesId}/sizes`);
      const data = await res.json();
      this.sizes = data;
      console.log('sosiz', data)
      this.generateVariants();
    },

    generateVariants() {
      if (!this.productData.designs.length || !this.sizes.length) return;

      const design = this.productData.designs[0]; // solo uno permitido
      const prefix = design.design_code;

      this.productData.variants = this.sizes.map(size => ({
        size_id: size.id,
        size_name: size.value,
        variant_code: `${prefix}${size.value}`,
      }));
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
