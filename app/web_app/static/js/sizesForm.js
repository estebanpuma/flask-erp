function sizesForm() {
  return {
    loading: false,
    serie: {
      name: '',
      category:'',
      start_size: '',
      end_size: '',
    },
    message: '',
    success: false,

    init() {
      // Opcional: lógica inicial
    },


    async submitForm() {
      this.loading = true;
      this.message = '';
      try {
        const res = await fetch('/api/v1/series', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.serie),
        });
        const data = await res.json();
        this.success = res.ok;
        this.message = this.success ? '✅ Serie creada' : (data.message || '❌ Error al crear serie');
        if (this.success) {
          this.serie.name = '';
          this.serie.code = '';
          this.serie.description = '';
          alert(this.message)
          window.location.href = '/products/series';
        }
      } catch (err) {
        console.error(err);
        this.success = false;
        this.message = '❌ Error de conexión';
        console.log(this.message)
      } finally {
        this.loading = false;
      }
    }
  }
}

