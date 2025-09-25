function jobCreatePage() {
  return {
    loading: false,
    form: {
      name: '',
      code:'',
      description: '',
      is_active: true
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
        const res = await fetch('/api/v1/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form),
        });
        const data = await res.json();
        this.success = res.ok;
        this.message = this.success ? '✅ Puesto creado' : (data.message || '❌ Error al crear');
        if (this.success) {
          this.form.name = '';
          this.form.code = '';
          this.form.description = '';
          this.form.is_active = true;
        }
      } catch (err) {
        console.error(err);
        this.success = false;
        this.message = '❌ Error de conexión';
      } finally {
        this.loading = false;
      }
    }
  }
}



function jobListPage() {
  return {
    loading: true,
    jobs: [],

    async init() {
      try {
        const res = await fetch('/api/v1/jobs');
        const data = await res.json();
        this.jobs = data;
      } catch (err) {
        console.error('Error al cargar puestos:', err);
      } finally {
        this.loading = false;
      }
    }
  };
}


function jobDetailPage(id) {
  return {
    job: {},
    workers: [],
    total_hours: 0,
    loading: true,

    init() {
      try {
        this.fetch_job()
      } catch (e) {
        console.error('Error al cargar detalle del puesto', e);
      } finally {
        this.loading = false;
      }
    },

    async fetch_job(){
        try{
            const resJob = await fetch(`/api/v1/jobs/${id}`);
            const data = await resJob.json();
            this.job = data;
            this.workers = data.workers
            console.log(data)
        }catch(e){
            console.error('Error al cargar detalle del puesto', e);
        }
    },



    calculateTotalHours(workers) {
      return workers.reduce((sum, w) => {
        return sum + (40 || 0);
      }, 0);
    }
  };
}

function jobEditPage(id) {
  return {
    loading: true,
    form: {},
    message: '',
    success: false,

    init() {
      try {
        this.fetchJob()
      } catch (e) {
        console.error('Error al cargar datos del puesto', e);
        this.message = '❌ Error al cargar datos';
        this.success = false;
      } finally {
        this.loading = false;
      }
    },

    async fetchJob(){
        try{
            const res = await fetch(`/api/v1/jobs/${id}`);
            const data = await res.json();
            this.form = data;
            console.log('form: ', data)
        }catch(err){
            console.error('error:', err)
        }
    },

    async submitForm() {
      this.loading = true;
      this.message = '';
      try {
        const res = await fetch(`/api/v1/jobs/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form),

        });
        console.log(this.form)
        const data = await res.json();
        this.success = res.ok;
        this.message = res.ok ? '✅ Puesto actualizado con éxito' : (data.message || '❌ Error al guardar');
        if(res.ok){
            window.location.href = `/workers/jobs/${id}`; // redirigir al listado
        }

      } catch (err) {
        console.error('Error al enviar', err);
        this.success = false;
        this.message = '❌ Error de conexión';
      } finally {
        this.loading = false;
      }
    }
  };
}
