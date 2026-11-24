/* Clausa: app instalável (PWA).
   - registra o service worker (funciona sem internet);
   - mostra os botões [data-instalar] só quando dá para instalar;
   - no Android/Chrome abre o pedido de instalação do próprio navegador;
   - no iPhone (Safari) explica o "Adicionar à Tela de Início". */
(function () {
  var st = document.createElement('style');
  st.textContent = '[data-instalar][hidden]{display:none!important}' +
    '.inst-veu{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.55);display:flex;align-items:flex-end;justify-content:center;padding:16px;padding-bottom:calc(16px + env(safe-area-inset-bottom,0px));animation:inst-in .2s ease}' +
    '.inst-box{max-width:420px;width:100%;background:#161617;color:#FAFAFA;border:1px solid #2A2A2D;border-radius:18px;padding:22px 22px 18px;font:400 15px/1.55 Inter,system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,.6)}' +
    '.inst-box h3{font:800 20px/1.2 "Inter Tight",Inter,sans-serif;letter-spacing:-.02em;margin:0 0 10px}' +
    '.inst-box ol{margin:0 0 16px;padding-left:20px;color:#C9C9CC}.inst-box li{margin:6px 0}.inst-box b{color:#FAFAFA}' +
    '.inst-box button{width:100%;font:600 15px Inter,sans-serif;border:0;border-radius:10px;padding:12px;background:#E2590B;color:#fff;cursor:pointer}' +
    '@keyframes inst-in{from{opacity:0}to{opacity:1}}';
  document.head.appendChild(st);

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }

  var pedido = null;
  var instalado = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  var ua = navigator.userAgent || '';
  var ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && 'ontouchend' in document);

  function botoes() { return [].slice.call(document.querySelectorAll('[data-instalar]')); }
  function mostrar(sim) { botoes().forEach(function (b) { b.hidden = !sim; }); }

  function dicaIOS() {
    var v = document.createElement('div'); v.className = 'inst-veu';
    v.innerHTML = '<div class="inst-box" role="dialog" aria-modal="true" aria-label="Instalar o Clausa">' +
      '<h3>Instalar o Clausa no iPhone</h3><ol>' +
      '<li>Toque em <b>Compartilhar</b> (o quadrado com a seta para cima) na barra do Safari.</li>' +
      '<li>Escolha <b>Adicionar à Tela de Início</b>.</li>' +
      '<li>Toque em <b>Adicionar</b>. O ícone do Clausa aparece junto dos seus apps.</li></ol>' +
      '<button type="button">Entendi</button></div>';
    function fechar() { v.remove(); }
    v.addEventListener('click', function (e) { if (e.target === v) fechar(); });
    v.querySelector('button').onclick = fechar;
    document.body.appendChild(v); v.querySelector('button').focus();
  }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); pedido = e; if (!instalado) mostrar(true);
  });
  window.addEventListener('appinstalled', function () { instalado = true; pedido = null; mostrar(false); });

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-instalar]');
    if (!b) return;
    e.preventDefault();
    if (pedido) {
      pedido.prompt();
      pedido.userChoice.then(function (r) { if (r.outcome === 'accepted') mostrar(false); pedido = null; });
    } else if (ios) { dicaIOS(); }
  });

  function iniciar() { mostrar(!instalado && ios); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
