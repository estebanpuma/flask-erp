/* ===== helpers.js | Guifer ERP ===== */
;(function (window) {
  'use strict'

  /* ---------- VALIDACIÓN ---------- */
  const isEmpty = val =>
    val == null ||
    (typeof val === 'string' && val.trim() === '') ||
    (Array.isArray(val) && val.length === 0) ||
    (typeof val === 'object' && !Array.isArray(val) && Object.keys(val).length === 0)

  const isEmail = str => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str.trim())
  const isCI    = str => /^\d{10}$/.test(str.trim())
  const isRUC   = str => /^\d{13}$/.test(str.trim())

  /* ---------- DINERO ---------- */
  const toCents   = amt => Math.round(Number(amt) * 100)
  const fromCents = c  => (c / 100).toFixed(2)
  const money     = c  => Number(fromCents(c))
  const moneyFmt  = amt =>
    Number(amt).toLocaleString('es-EC', { style:'currency', currency:'USD' })
  const round     = (num, d=2) =>
    Math.round((Number(num)+Number.EPSILON)*10**d)/10**d

  /* ---------- FECHAS ---------- */
  const today  = () => new Date()
  const addDays = (date, days)=>{
    const d=new Date(date); d.setDate(d.getDate()+Number(days)); return d }
  const fmtDate = date=>{
    const d=new Date(date)
    return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`
  }

  /* ---------- ARRAYS / OBJ ---------- */
  const findById  = (a,id)=>a.find(e=>e.id===id)
  const removeById= (a,id)=>a.filter(e=>e.id!==id)
  const sumBy     = (a,p)=>a.reduce((acc,e)=>acc+Number(e[p]||0),0)
  const groupBy   = (a,k)=>a.reduce((acc,e)=>
                         ((acc[e[k]]=acc[e[k]]||[]).push(e),acc),{})
  const deepClone = obj=>JSON.parse(JSON.stringify(obj))

  /* ---------- UI ---------- */
  const showToast=(msg,type='info',delay=3000)=>{
    const t=document.createElement('div')
    t.className=`toast align-items-center text-bg-${type} border-0`
    t.role='alert'
    t.innerHTML=`<div class="d-flex">
       <div class="toast-body">${msg}</div>
       <button class="btn-close btn-close-white me-2 m-auto"
               data-bs-dismiss="toast"></button></div>`
    document.body.appendChild(t)
    const bs=bootstrap.Toast.getOrCreateInstance(t,{delay})
    bs.show(); t.addEventListener('hidden.bs.toast',()=>t.remove())
  }
  const badgeClass=st=>({
    Aprobada:'badge bg-success',
    Rechazada:'badge bg-danger',
    Pendiente:'badge bg-warning text-dark'
  }[st]||'badge bg-secondary')

  /* ---------- FETCH ---------- */
  async function apiFetch(method,path,body=null,opts={}){
    const cfg={method,headers:{'Content-Type':'application/json',...opts.headers},...opts}
    if(body!==null) cfg.body=JSON.stringify(body)
    const res=await fetch(`/api/v1/${path}`,cfg)
    if(res.status===204) return null
    const data=await res.json().catch(()=>null)
    if(!res.ok){
      const msg=data?.errors??data?.message??res.statusText
      throw new Error(`Error:${res.status} ${msg}`)
    }
    return data
  }


  /* ---------- EXPOSE ---------- */
  window.guifer = window.guifer || {}
  window.guifer.helpers = window.guifer.helpers || {};
  Object.assign(window.guifer.helpers, {
  
    validate:{ isEmpty,isEmail,isCI,isRUC },
    money:{ toCents,fromCents,money,moneyFmt,round },
    date:{ today,addDays,fmtDate },
    array:{ findById,removeById,sumBy,groupBy,deepClone },
    ui:{ showToast,badgeClass },
    fetch: {apiFetch},
  })
  console.log(window.guifer.helpers.fetch)
})(window)
