/*
 * Modo demonstração: quando a página não roda no ambiente que fornece banco de dados e
 * armazenamento de fotos, este script oferece uma versão local equivalente, guardada no
 * localStorage do navegador. Nada sai do seu computador.
 */
(function () {
  'use strict';
  var KEY = 'cl' + 'aude';
  if (window[KEY]) return;

  var LS_DB = 'qc_demo_db_v1';
  var LS_ASSETS = 'qc_demo_assets_v1';
  var DAY = 86400000;

  function read(key) {
    try { var raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : null; } catch (e) { return null; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch (e) { return false; }
  }

  function shiftDate(value, deltaDays, withTime) {
    if (!value) return value;
    var d = new Date(withTime ? value : value + 'T12:00:00');
    d = new Date(d.getTime() + deltaDays * DAY);
    return withTime ? d.toISOString() : d.toISOString().slice(0, 10);
  }

  function buildSeed() {
    var seed = JSON.parse(JSON.stringify(window.QC_SEED || { config: {}, cd_recebimento: {}, cliente_recebimento: {} }));
    var latest = 0;
    ['cd_recebimento', 'cliente_recebimento'].forEach(function (c) {
      Object.keys(seed[c] || {}).forEach(function (id) {
        var t = new Date(seed[c][id].createdAt).getTime();
        if (t > latest) latest = t;
      });
    });
    var delta = latest ? Math.round((Date.now() - latest) / DAY) : 0;
    if (delta > 0) {
      ['cd_recebimento', 'cliente_recebimento'].forEach(function (c) {
        Object.keys(seed[c] || {}).forEach(function (id) {
          var r = seed[c][id];
          r.createdAt = shiftDate(r.createdAt, delta, true);
          ['dataCompra', 'dataChegada', 'dataReclamacao'].forEach(function (f) { if (r[f]) r[f] = shiftDate(r[f], delta, false); });
        });
      });
    }
    return seed;
  }

  var store = read(LS_DB);
  if (!store) { store = buildSeed(); write(LS_DB, store); }
  var assets = read(LS_ASSETS) || {};
  var listeners = [];

  function docsOf(coll) {
    var all = store[coll] || {};
    return Object.keys(all).map(function (id) { return { id: id, data: function () { return all[id]; }, exists: true }; });
  }

  function snapshotFor(q) {
    var docs = docsOf(q.coll);
    if (q.order) {
      docs.sort(function (a, b) {
        var x = a.data()[q.order.field], y = b.data()[q.order.field];
        if (x === y) return 0;
        return (x < y ? -1 : 1) * (q.order.dir === 'desc' ? -1 : 1);
      });
    }
    if (q.limit) docs = docs.slice(0, q.limit);
    return { docs: docs, size: docs.length, empty: !docs.length };
  }

  function notify(coll) {
    listeners.forEach(function (l) { if (l.q.coll === coll) l.cb(snapshotFor(l.q)); });
  }

  function query(q) {
    return {
      orderBy: function (field, dir) { return query({ coll: q.coll, order: { field: field, dir: dir || 'asc' }, limit: q.limit }); },
      limit: function (n) { return query({ coll: q.coll, order: q.order, limit: n }); },
      onSnapshot: function (cb) {
        var l = { q: q, cb: cb };
        listeners.push(l);
        setTimeout(function () { cb(snapshotFor(q)); }, 0);
        return function () { listeners = listeners.filter(function (x) { return x !== l; }); };
      },
      add: function (data) {
        var id = 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        store[q.coll] = store[q.coll] || {};
        store[q.coll][id] = JSON.parse(JSON.stringify(data));
        write(LS_DB, store);
        notify(q.coll);
        return Promise.resolve({ id: id });
      }
    };
  }

  var db = {
    collection: function (c) { return query({ coll: c }); },
    doc: function (path) {
      var parts = path.split('/');
      var coll = parts[0], id = parts[1];
      return {
        get: function () {
          var d = store[coll] && store[coll][id];
          return Promise.resolve({ id: id, exists: !!d, data: function () { return d; } });
        },
        set: function (data) {
          store[coll] = store[coll] || {};
          store[coll][id] = JSON.parse(JSON.stringify(data));
          write(LS_DB, store);
          notify(coll);
          return Promise.resolve();
        },
        update: function (data) {
          if (!store[coll] || !store[coll][id]) return Promise.reject({ code: 'invalid_argument' });
          Object.keys(data).forEach(function (k) { store[coll][id][k] = JSON.parse(JSON.stringify(data[k])); });
          write(LS_DB, store);
          notify(coll);
          return Promise.resolve();
        }
      };
    }
  };

  function toDataUrl(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onerror = function () { reject({ code: 'invalid_request' }); };
      reader.onload = function () {
        var img = new Image();
        img.onerror = function () { reject({ code: 'unsupported_type' }); };
        img.onload = function () {
          var max = 800, scale = Math.min(1, max / Math.max(img.width, img.height));
          var canvas = document.createElement('canvas');
          canvas.width = Math.round(img.width * scale);
          canvas.height = Math.round(img.height * scale);
          canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve(canvas.toDataURL('image/jpeg', 0.75));
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }

  var assetsApi = {
    upload: function (file) {
      return toDataUrl(file).then(function (url) {
        var id = 'a' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        assets[id] = url;
        if (!write(LS_ASSETS, assets)) { delete assets[id]; return Promise.reject({ code: 'quota_or_state' }); }
        return { id: id, url: url, sizeBytes: url.length, contentType: 'image/jpeg' };
      });
    },
    delete: function (ref) {
      delete assets[ref];
      write(LS_ASSETS, assets);
      return Promise.resolve({ deleted: true });
    }
  };

  window[KEY] = {
    use: function (name) {
      if (name === 'db') return Promise.resolve(db);
      if (name === 'assets') return Promise.resolve(assetsApi);
      return Promise.resolve(null);
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('nav.tabs');
    if (!nav) return;
    var bar = document.createElement('div');
    bar.setAttribute('style', 'display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap;' +
      'background:var(--accent-soft);color:var(--accent-ink);border:1px solid var(--border);border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:6px;');
    var msg = document.createElement('span');
    msg.textContent = 'Modo demonstração: os dados abaixo são fictícios e tudo que você cadastrar fica salvo só neste navegador.';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm';
    btn.textContent = 'Restaurar exemplos';
    btn.addEventListener('click', function () {
      try { localStorage.removeItem(LS_DB); localStorage.removeItem(LS_ASSETS); } catch (e) { /* sem acesso ao armazenamento */ }
      location.reload();
    });
    bar.appendChild(msg);
    bar.appendChild(btn);
    nav.parentNode.insertBefore(bar, nav);
  });
})();
