function lineList() {
  return {
    lines: [],

    init() {
      this.fetchLines()
    },

    async fetchLines(){
      try{
        const res = await fetch('/api/v1/product-lines');
        const data = await res.json();
        this.lines = data;
        console.log('lines', this.lines)
      }catch(err){
        console.error('Error: ',err)
      }
    },
  }
}


function lineDetail(line_id) {
  return {
    line: {},
    loading: true,
    init() {
      try {
        this.fetchLine();
      } catch (err) {
        alert('Error al cargar la línea');
      } finally {
        this.loading = false;
      }
    },

    async fetchLine(){
      try{
        const res = await fetch(`/api/v1/product-lines/${line_id}`);
        const data = await res.json();
        console.log('data:', data)
        this.line = data;
        console.log('lines', this.line)
      }catch(err){
        console.error('Error: ',err)
      }
    },
  }
}


function createLine() {
  return {
    line: { name: '', code:'',description: '' },
    existing_code:false,
    error:'',
    init() {
      // Puedes inicializar campos por defecto si deseas
    },

    async checkCode(){
      try{
        const res = await fetch(`/api/v1/product-lines?code=${this.line.code.toUpperCase()}`);
        const data = await res.json();
        console.log('data:', data)

        if (data.code){
          this.existing_code = true;
          return true
        }
        else{
          this.existing_code = false;
          return false
        }

      }catch(err){
        console.error('Error: ',err)
      }
    },

    async createLine() {
      try {
        const res = await fetch('/api/v1/product-lines', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.line)
        });

        if (!res.ok) throw new Error('Error al crear línea');
        window.location.href = '/products/lines';
      } catch (error) {
        alert(error.message);
      }
    }
  }
}




function sublineList() {
  return {
    sublines: [],

    init() {
      this.fetchsubLines()
    },

    async fetchsubLines(){
      try{
        const res = await fetch('/api/v1/product-sublines');
        const data = await res.json();
        this.sublines = data;
        console.log('sublines', this.sublines)
      }catch(err){
        console.error('Error: ',err)
      }
    },
  }
}


function sublineDetail(subline_id) {
  return {
    subline: {},
    loading: true,
    init() {
      try {
        this.fetchsubLine();
      } catch (err) {
        alert('Error al cargar la línea');
      } finally {
        this.loading = false;
      }
    },

    async fetchsubLine(){
      try{
        const res = await fetch(`/api/v1/product-sublines/${subline_id}`);
        const data = await res.json();
        console.log('data:', data)
        this.subline = data;
        console.log('sublines', this.subline)
      }catch(err){
        console.error('Error: ',err)
      }
    },
  }
}


function createSubLine() {
  return {
    subline: { name: '', code:'',description: '' },
    existing_code:false,
    init() {
      // Puedes inicializar campos por defecto si deseas
    },

    async checkCode(){
      try{
        const res = await fetch(`/api/v1/product-sublines?code=${this.subline.code.toUpperCase()}`);
        const data = await res.json();
        console.log('data:', data)

        if (data.length>0){
          console.log('esxr: ', this.existing_code)
          this.existing_code = true;
          console.log('esxr afet: ', this.existing_code)
          return true
        }
        else{
          this.existing_code = false;
          return false
        }

      }catch(err){
        console.error('Error: ',err)
      }
    },

    async createsubLine() {
      try {
        const res = await fetch('/api/v1/product-sublines', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.subline)
        });

        if (!res.ok) throw new Error('Error al crear sublínea');
        window.location.href = '/products/sublines';
      } catch (error) {
        alert(error.message);
      }
    }
  }
}
