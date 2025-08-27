;(function (w) {
  function modal() {
    return {
      isOpen: false,
      toggle () { this.isOpen = !this.isOpen },
      closeModal () { this.isOpen = false }
    }
  }

  w.guifer = w.guifer || {}
  w.guifer.components = w.guifer.components || {}
  w.guifer.components.modal = modal
})(window)
