function productsList() {
  return {
    products: [],
    loading: false,
    

    async init() {
      this.loading = true;
      try {
        const res = await fetch('/api/v1/products');
        const data = await res.json();
        this.products = data;
      } catch (err) {
        console.error('Error al cargar productos', err);
      }
      this.loading = false;
    }
  };
}


function productWizard() {
  return {
    step: 1,
    loading: false,
    success: false,
    error: '',
    product: {
      name: '',
      code: '',
      line_id: '',
      subline_id: '',
    },
    designs: [
      {
        name: '',
        code_suffix: '',
        series_id: '',
        materials: []
      }
    ],
    
    lines: [],
    sublines: [],
    designCodeStatus: '', // '', 'available', 'taken'

    async init(){

    },


    fetchNextCode() {
      const letter = this.product.code_letter?.toUpperCase();
      if (!letter || !/^[A-Z]$/.test(letter)) {
        this.product.code = '';
        return;
      }

      fetch(`/api/products/next-code?letter=${letter}`)
        .then(res => res.json())
        .then(data => {
          if (data.code) {
            this.product.code = data.code;
          } else {
            this.error = data.message || 'No se pudo generar código.';
            this.product.code = '';
          }
        })
        .catch(() => {
          this.error = 'Error al verificar el código.';
          this.product.code = '';
        });
    },

    async fetchLines(){
        try {
                const res = await fetch('/api/v1/product-lines');
                const data = await res.json();
                this.products = data;
            } catch (err) {
                console.error('Error al cargar lineas', err);
            }
    },


    async checkDesignCode() {
        const fullCode = this.product.code + this.newDesign.code; // ej. 'C001' + 'NE'
        try {
            const res = await fetch(`/api/v1/product-designs?code=${fullCode}`);
            const data = await res.json();
            this.designCodeStatus = data[0].id ? 'taken' : 'available';
        } catch (err) {
            console.error('Error al verificar código de diseño', err);
        }
        },

    nextStep() {
      if (this.step === 1 && (!this.product.name || !this.product.code)) {
        this.error = 'Nombre y código del producto son obligatorios';
        return;
      }
      this.error = '';
      this.step++;
    },

    submit() {
      this.loading = true;
      fetch('/api/v1/products', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          ...this.product,
          designs: this.designs
        })
      })
        .then(res => res.json())
        .then(data => {
          this.loading = false;
          if (data.success) {
            this.success = true;
            setTimeout(() => window.location.href = '/products', 1500);
          } else {
            this.error = data.message || 'Error al guardar producto';
          }
        })
        .catch(err => {
          this.loading = false;
          this.error = 'Error de red';
          console.error(err);
        });
    }
  };

  
}

