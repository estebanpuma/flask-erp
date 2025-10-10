function productWizard({  startStep = null } = {}) {
  return {
    // Configuración inicial
    startStep: startStep,
    step: startStep || 1, // El paso actual del wizard
    totalSteps: 4, // 1: Básico, 2: Diseño/Imágenes, 3: Variantes, 4: Materiales

    error_code: '',

    // --- ESTADO Y DATOS ---
    // Payload central
    productData: {
      code: '',
      name: '',
      old_code:null,
      line_id: null,
      subline_id: null,
      target_id: null,
      collection_id: null,
      description: '',
      designs: [], // Este se simplificará o reemplazará
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
    // Nuevo: gestiona colores con sus imágenes asociadas
    selectedColors: [], // Estructura: [{id, name, code, images: [], primary_image: null}]

    existingDesignCodes: null,
    newDesignCode: null,
    isDuplicateDesign: true,

    init() {
      console.log('init:', this.step)
      console.log('product_id:', this.productId)
      this.fetchLines();
      this.fetchSubLines();
      this.fetchTargets();
      // Carga pasos necesarios según startStep
      if (this.step <= 2) {
        this.fetchColors();
      }
      if (this.step <= 3) this.fetchSeries();

    },

    // --- PASO 1: Datos Básicos y Clasificación ---

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
                const res = await fetch(`/api/v1/product-collections?${params}`);
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
        this.setName();
        this.checkCode();
      } catch {
        this.error = 'Error al generar código.';
      }
    },

    setName(){
      console.log('set name')
        const selectedCollection = this.collections.find(c => c.id === Number(this.productData.collection_id));
      console.log('selected collection:', selectedCollection);
      if (selectedCollection) {
        let name = selectedCollection.name;
        console.log('name collection:', name);

        if (this.productData.code) {
          name = name + ' ' + this.productData.code.slice(-3);
        }
        this.productData.name = name;
        console.log('name:', this.productData.name);
      }
    },

    async checkCode() {
      try{
        const res = await window.guifer.helpers.fetch.apiFetch('GET', '/products?code=' + this.productData.code);
        if(res && res.length>0){
          this.error_code = 'Ya existe un porducto con este codigo'
        }else{
          this.error_code = ''
        }
      }catch(err){
        console.error(err)
      }
    },


  // --- PASO 2: Diseño (Colores e Imágenes) ---

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
        this.removeColor(color.id);
      } else {
        // Añadimos el color con un espacio para sus imágenes
        this.selectedColors.push({
            id: color.id,
            name: color.name,
            code: color.code,
            images: [] // Array para los archivos de imagen
        });
      }
    },

    isColorSelected(id) {
      return this.selectedColors.some(c => c.id === id);
    },

    removeColor(color) {
      this.selectedColors = this.selectedColors.filter(c => c.id !== color.id);
    },

    // Nueva lógica para manejar la subida de imágenes por color
    handleImageUpload(event, colorId) {
        const color = this.selectedColors.find(c => c.id === colorId);
        if (!color) return;

        const files = Array.from(event.target.files);

        // Creamos previews para la UI y guardamos el archivo
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                color.images.push({
                    file: file, // El objeto File real para el upload
                    previewUrl: e.target.result, // URL para mostrar en la UI
                    is_primary: color.images.length === 0 // La primera es primaria por defecto
                });
            };
            reader.readAsDataURL(file);
        });
        event.target.value = ''; // Resetea el input para poder subir el mismo archivo de nuevo
    },

    removeImage(colorId, imageIndex) {
        const color = this.selectedColors.find(c => c.id === colorId);
        if (color) {
            color.images.splice(imageIndex, 1);
        }
    },

    setPrimaryImage(colorId, imageIndex) {
        const color = this.selectedColors.find(c => c.id === colorId);
        if (color) {
            color.images.forEach((img, idx) => img.is_primary = (idx === imageIndex));
        }
    },

    //-----------------immges-----------------
  images: [], dragging: null, hoverId: null,
  async upload(e){
      const files = e.target.files || e.dataTransfer?.files || [];
      for(const f of files){
        const fd = new FormData();
        fd.append('image', f);
        await fetch(`/api/v1/product-designs/${this.designId}/images`, { method:'POST', body: fd });
      }
      await this.fetch();
      if(e.target?.value !== undefined) e.target.value = '';
    },
    handleDrop(e){ this.upload(e) },

    dragStart(img){ this.dragging = img },
    async dropOn(target){
      if(!this.dragging || this.dragging.id===target.id) return;
      const arr = this._reordered(this.dragging, target);
      await fetch(`/api/v1/product-designs/${this.designId}/images/reorder`,{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ ordered_ids: arr.map(i=>i.id) })
      });
      this.dragging = null;
      await this.fetch();
    },
    _reordered(drag, drop){
      const arr = this.images.slice();
      const from = arr.findIndex(i=>i.id===drag.id);
      const to   = arr.findIndex(i=>i.id===drop.id);
      arr.splice(to,0,arr.splice(from,1)[0]);
      return arr;
    },
    // --- PASO 3: Variantes (Tallas) ---

    sizeSeries: [],
    selectedSeriesId: '',
    generatedVariants:[],
    selectedSerie:{},


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
        this.productData.variants = [];
        this.generatedVariants =[];
        return;
      }
      this.selectedSerie = this.sizeSeries.find(s => s.id === this.selectedSeriesId);


      const res = await fetch(`/api/v1/series/${this.selectedSeriesId}/sizes`);
      const sizes = await res.json();
      this.generateVariants(sizes);
    },

    removeSerie() {
      this.selectedSeriesId = '';
      this.productData.variants = [];
      this.selectedSerieSizes = [];
      this.selectedSerie = '';
    },

    generateVariants(sizes) {
      // Ahora depende de selectedColors, no de designs
      if (!this.selectedColors.length || !sizes.length) {
        this.productData.variants = [];
        this.generatedVariants = [];
        return;
      }

      this.generatedVariants = [];
      this.selectedColors.forEach(color => {
        const prefix = this.productData.code + color.code;
        sizes.forEach(size => {
            this.generatedVariants.push({
                size_id: size.id, size_name: size.value, color_id: color.id, color_name: color.name,
                variant_code: `${prefix}${size.value}`, check: true,
            });
        });
      });
    },

    addVariants(){
      let selected = this.generatedVariants.filter(s => s.check);
      this.productData.variants = selected
      console.info('variants selected: ', this.productData.variants)
    },




    // --- PASO 4: Materiales (BOM) ---

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



    // --- NAVEGACIÓN Y VALIDACIÓN DEL WIZARD ---

    isStep1Valid() {
      // Validación estricta para el paso 1
      const pd = this.productData;
      return pd.name && pd.line_id && pd.target_id && pd.collection_id && pd.code && !this.error_code;
    },

    isStep2Valid() {
      // Validación para el paso 2: al menos un color y sin duplicados.
      // Y que cada color seleccionado tenga al menos una imagen.
      return this.selectedColors.length > 0 &&
             this.selectedColors.every(c => c.images && c.images.length > 0);
    },

    isStep3Valid() {
        // Validación para el paso 3: al menos una variante seleccionada.
        return this.productData.variants.length > 0;
    },

    isStep4Valid() {
        // Validación para el paso 4: al menos un material en la lista.
        return this.productData.materials.length > 0;
    },

    nextStep() {
      // Validar antes de avanzar
      if (this.step === 1 && !this.isStep1Valid()) {
        this.error = "Debes completar todos los campos de clasificación y asegurarte que el código no esté duplicado.";
        return;
      }
      if (this.step === 2 && !this.isStep2Valid()) {
        this.error = "Debes seleccionar al menos un color y subir al menos una imagen para cada color seleccionado.";
        return;
      }

      // Añadir validaciones para otros pasos aquí...

      this.error = ''; // Limpiar error si todo está bien
      if (this.step < this.totalSteps) this.step++;
    },

    prevStep() {
      if (this.step > 1 && this.step > (this.startStep || 1)) this.step--;

    },

    resetWizard() {
      if (confirm('¿Cancelar creación del producto?')) {
        window.location.href = '/products';
      }
    },

    // --- SUBMIT FINAL ---

    async submitFinal() {
      if (!this.isStep4Valid()) {
          this.error = "El producto debe tener al menos un material definido para poder ser fabricado.";
          return;
      }
      try {
        const formData = new FormData();

        // 1. Añadir datos JSON del producto
        const productPayload = {
            name: this.productData.name,
            code: this.productData.code,
            line_id: this.productData.line_id,
            subline_id: this.productData.subline_id,
            target_id: this.productData.target_id,
            collection_id: this.productData.collection_id,
            description: this.productData.description,
            variants: this.productData.variants,
            materials: this.productData.materials,
            // Incluimos los colores seleccionados para que el backend sepa qué crear
            colors: this.selectedColors.map(c => ({ id: c.id }))
        };
        formData.append('data', JSON.stringify(productPayload));

        // 2. Añadir imágenes, asociándolas a su color
        this.selectedColors.forEach(color => {
            color.images.forEach((image, index) => {
                // Usamos una clave estructurada: images_COLORID_IMAGENAME
                formData.append(`images_${color.id}`, image.file, image.file.name);
                if (image.is_primary) {
                    formData.append('primary_image', `color_${color.id}_${image.file.name}`);
                }
            });
        });

        // 3. Enviar todo como multipart/form-data
        const res = await fetch('/api/v1/products', {
            method: 'POST',
            body: formData, // No se necesita 'Content-Type', el navegador lo pone solo
        });

        const data = await res.json();
        if (res.ok) {
            alert('✅ Producto creado correctamente');
            window.location.href = `/products/${data.id}`;
        }



      } catch (e) {
        alert('❌ Error de conexión');
      }
    }
  };
}
