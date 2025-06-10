function clientSearch() {
  return {
    query: '',
    results: [],
    showResults: false,

    reset() {
      this.query = '';
      this.results = [];
      this.showResults = false;
    },

    async searchClients() {
      if (this.query.length < 3) {
        this.results = [];
        return;
      }

      try {
        const res = await fetch(`/api/v1/clients/search?q=${encodeURIComponent(this.query)}`);
        const data = await res.json();
        this.results = data;
        console.log(this.results)
        this.showResults = true;
      } catch {
        this.results = [];
      }
    },

    selectClient(client) {
      this.query = client.name;
      this.showResults = false;

      // Evento personalizado para notificar selección (se puede escuchar con Alpine o JS)
      const event = new CustomEvent('client-selected', { detail: client });
      window.dispatchEvent(event);
    }
  }
}
