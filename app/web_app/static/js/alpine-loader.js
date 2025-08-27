// /static/js/alpine-loader.js
(function () {

  
  // --- util: carga un <script> y devuelve Promise
  function loadScript(src) {
    return new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = src;
      s.async = true; // ← permite descargas en paralelo
      s.onload = () => { res(src); };
      s.onerror = () => { console.error('[loader] FAIL', src); rej(new Error(src)); };
      document.head.appendChild(s);
    });
  }

  // --- 2) Mapa simple: nombre → ruta de script
  const COMPONENTS = {
    inputs:   '/static/js/components/inputs.js',
    buttons:  '/static/js/components/buttons.js',
    modals:   '/static/js/components/modals.js',
    status:   '/static/js/components/status.js', 

  };

  // --- 3) Orquestación: carga en paralelo y arranca Alpine al final
  (async () => {
    try {
      // Helpers/Stores/Hooks que quieres siempre (cárgalos ya en paralelo)
      const ALWAYS = [
        '/static/js/helpers.js',
        '/static/js/components.js'
      ]

      // 🔹 Dispara todas las descargas en paralelo
      const toLoad = Array.from(
        new Set([
          ...ALWAYS,
          ...Object.values(COMPONENTS) // ← ¡aquí va Object.values!
        ])
      );

      // 2) Dispara todas las descargas en paralelo
      await Promise.all(toLoad.map(loadScript));

      // 🔹 Por último: Alpine (con fallback local)
      try {
        await loadScript('https://cdn.jsdelivr.net/npm/alpinejs@3.13.5/dist/cdn.min.js');
      } catch {
        await loadScript('/static/js/alpine/alpine.min.js');
      }

      console.log('[loader] Alpine loaded. Done ✅');
    } catch (e) {
      console.error('[loader] error', e);
    }
  })();
})();
