function alertComp(initProps = {}) {
  return {
    msg: 'Alerta',
    type: 'primary',
    icon: 'info-circle',
    visible: false,
    _timeoutId: null,
    _iconsByType(t) {
      return ({ success:'check-circle', warning:'exclamation-triangle', danger:'exclamation-triangle',
                info:'info-circle', primary:'info-circle', secondary:'info-circle', light:'info-circle', dark:'info-circle' })[t] || 'info-circle';
    },
    show({ msg='Alerta', type='primary', timeout=0 } = {}) {
      this.msg = String(msg);
      this.type = String(type);
      this.icon = this._iconsByType(this.type);
      this.visible = true;
      if (this._timeoutId) clearTimeout(this._timeoutId);
      if (timeout > 0) this._timeoutId = setTimeout(() => this.hide(), timeout);
    },
    hide() {
      this.visible = false;
      if (this._timeoutId) clearTimeout(this._timeoutId);
      this._timeoutId = null;
    },
    init() {
      if (initProps.msg) this.show(initProps);
    }
  }
}
   document.addEventListener('alpine:init', () => {
        Alpine.data('alertComp', alertComp);
    });
