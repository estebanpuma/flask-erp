function collectionDetail(collection_id) {
  return {
    collection: {},
    loading: true,
    init() {
      try {
        this.fetchcollection();
      } catch (err) {
        alert('Error al cargar la línea');
      } finally {
        this.loading = false;
      }
    },

    async fetchcollection(){
      try{
        const res = await fetch(`/api/v1/product-collections/${collection_id}`);
        const data = await res.json();
        console.log('data:', data)
        this.collection = data;
        console.log('lines', this.collection)
      }catch(err){
        console.error('Error: ',err)
      }
    },
  }
}


function createCollection() {
  return {
    collection: { line_id: '', subline_id: '', target_id: '', name: '', description: '' },
    existing_code: false,
    error: '',
    lines: [],
    sublines: [],
    targets: [],
    preview_code: '',

    init() {
      this.fetchLines();
      this.fetchSublines();
      this.fetchTargets();
    },

    async fetchLines() {
      try {
        const res = await fetch(`/api/v1/product-lines`);
        this.lines = await res.json();
      } catch (err) {
        console.error('Error fetching lines:', err);
      }
    },

    async fetchSublines() {
      try {
        const res = await fetch(`/api/v1/product-sublines`);
        this.sublines = await res.json();
      } catch (err) {
        console.error('Error fetching sublines:', err);
      }
    },

    async fetchTargets() {
      try {
        const res = await fetch(`/api/v1/product-targets`);
        this.targets = await res.json();
      } catch (err) {
        console.error('Error fetching targets:', err);
      }
    },

    async previewCode() {
      try {
        const params = new URLSearchParams({
          line_id: this.collection.line_id,
          subline_id: this.collection.subline_id,
          target_id: this.collection.target_id
        });
        const res = await fetch(`/api/v1/product-collections/preview-code?${params}`);
        const data = await res.json();
        this.preview_code = data.preview_code;
        return data.preview_code;
      } catch (err) {
        console.error('Error previewing code:', err);
      }
    },

    async createCollection() {
      try {
        const payload = {
          ...this.collection,
          line_id: this.collection.line_id ? parseInt(this.collection.line_id) : null,
          subline_id: this.collection.subline_id ? parseInt(this.collection.subline_id) : null,
          target_id: this.collection.target_id ? parseInt(this.collection.target_id) : null,
        };
        const res = await fetch('/api/v1/product-collections', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Error creando la colección');
        window.location.href = '/products/collections';
      } catch (error) {
        console.error('Error creando colección:', error);
        alert('Ocurrió un error al crear la colección. Revisa la consola.');
      }
    }
  }
}

