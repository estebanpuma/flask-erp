function workerCreate() {
  return {
    form: {
      ci: '',
      first_name: '',
      last_name: '',
      job_id: '',
      phone: '',
      worker_type: '',
      hour_rate_normal: 1,
      hour_rate_overtime: 1,
      notes: ''
    },
    jobs: [],

    init() {
      this.fetchJobs();
    },

    async fetchJobs() {
      try {
        const res = await fetch('/api/v1/jobs');
        const data = await res.json();
        this.jobs = data || [];
      } catch (err) {
        console.error('Error cargando cargos:', err);
      }
    },

    async createWorker() {
      try {
        const res = await fetch('/api/v1/workers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        if (!res.ok) {
          const errorData = await res.json();
          console.error(errorData);
          alert(errorData.message || 'Error al guardar operario.');
          return;
        }

        window.location.href = '/workers'; // redirigir al listado
      } catch (err) {
        console.error(err);
        alert('Error inesperado al guardar operario.');
      }
    }
  };
}



function workerList() {
  return {
    workers: [],
    loading: true,
    error: null,
    viewMode: 'table',

    init() {
        if (window.innerWidth < 768) {
        this.viewMode = 'cards';
        }else{
          this.viewMode ='table'
        }
      this.fetchWorkers();
    },
    

    async fetchWorkers() {
      this.loading = true;
      try {
        const res = await fetch('/api/v1/workers');
        const data = await res.json();
        this.workers = data || [];
      } catch (err) {
        console.error('Error al cargar operarios:', err);
        this.error = 'No se pudo cargar la lista de operarios.';
      } finally {
        this.loading = false;
      }
    }
  };
}



function workerDetail(worker_id) {
  return {
    worker: null,
    loading: true,
    error: null,

    init() {
      this.fetchWorker();
    },

    async fetchWorker() {
      this.loading = true;
      try {
        const res = await fetch(`/api/v1/workers/${worker_id}`);
        if (!res.ok) throw new Error('No se encontró el operario.');
        const data = await res.json();
        this.worker = data;
      } catch (err) {
        console.error(err);
        this.error = 'Error al cargar el perfil del operario.';
      } finally {
        this.loading = false;
      }
    }
  };
}




function workerEditPage(id) {
  return {
    worker_id: id,
    form: {},
    jobs: [],
    loading: true,
    success: false,
    message: '',

    async init() {
      try {
        const [workerRes, jobsRes] = await Promise.all([
          fetch(`/api/v1/workers/${this.worker_id}`),
          fetch(`/api/v1/jobs`)
        ]);
        this.form = await workerRes.json();
        this.jobs = await jobsRes.json();
        this.loading = false;
      } catch (e) {
        this.message = '❌ Error al cargar datos';
        this.success = false;
        this.loading = false;
      }
    },

    async submitForm() {
      this.loading = true;
      try {
        const res = await fetch(`/api/v1/workers/${this.worker_id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form),
        });
        const data = await res.json();
        this.success = res.ok;
        this.message = res.ok ? '✅ Actualizado con éxito' : (data.message || '❌ Error al guardar');
        window.location.href = `/workers/${this.worker_id}`; // redirigir al listado
      } catch (e) {
        this.success = false;
        this.message = '❌ Error de conexión';
      } finally {
        this.loading = false;
      }
    }
  }
}

