"""Dashboard HTML and API for lead nurture monitoring."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lead Nurture Dashboard - DobotAI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}
.container{max-width:1200px;margin:0 auto}
.header{background:white;padding:30px;border-radius:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1);margin-bottom:30px}
.header h1{color:#2d3748;font-size:28px;margin-bottom:8px}
.header p{color:#718096;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:30px}
.stat-card{background:white;padding:20px;border-radius:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}
.stat-card h3{color:#718096;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px}
.stat-card .number{color:#2d3748;font-size:32px;font-weight:bold}
.leads-container{background:white;border-radius:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1);overflow:hidden}
.leads-header{background:#f7fafc;padding:20px;border-bottom:1px solid #e2e8f0}
.leads-header h2{color:#2d3748;font-size:20px}
.lead-card{padding:20px;border-bottom:1px solid #e2e8f0;transition:background 0.2s}
.lead-card:hover{background:#f7fafc}
.lead-card:last-child{border-bottom:none}
.lead-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.lead-info h3{color:#2d3748;font-size:18px;margin-bottom:4px}
.lead-info p{color:#718096;font-size:14px}
.lead-actions{display:flex;gap:8px;align-items:center}
.lead-badge{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;background:#48bb78;color:white}
.cancel-btn{padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;background:#e53e3e;color:white;border:none;cursor:pointer;transition:background 0.2s}
.cancel-btn:hover{background:#c53030}
.cancel-btn:disabled{background:#cbd5e0;cursor:not-allowed}
.email-progress{display:flex;gap:8px;margin-top:12px}
.email-step{flex:1;height:8px;background:#e2e8f0;border-radius:4px}
.email-step.sent{background:#48bb78}
.email-details{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #e2e8f0}
.email-detail{font-size:12px}
.email-detail .label{color:#718096;margin-bottom:2px}
.email-detail .value{color:#2d3748;font-weight:500}
.empty-state{padding:60px 20px;text-align:center;color:#718096}
.empty-state h3{font-size:20px;margin-bottom:8px}
.loading{text-align:center;padding:40px;color:#718096}
</style></head><body>
<div class="container">
<div class="header"><h1>Lead Nurture Dashboard</h1><p>Monitor active leads in the email nurture workflow</p></div>
<div class="stats"><div class="stat-card"><h3>Active Leads</h3><div class="number" id="active-count">-</div></div>
<div class="stat-card"><h3>Emails Sent</h3><div class="number" id="emails-sent">-</div></div>
<div class="stat-card"><h3>Emails Scheduled</h3><div class="number" id="emails-scheduled">-</div></div></div>
<div class="leads-container"><div class="leads-header"><h2>Active Leads</h2></div>
<div id="leads-list" class="loading">Loading...</div></div></div>
<script>
function formatDate(d){const dt=new Date(d);return dt.toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit',hour12:true})}
function formatRelative(d){const dt=new Date(d),now=new Date(),diff=dt-now,m=Math.floor(diff/60000),h=Math.floor(diff/3600000);return diff<0?'Past':m<60?`${m}m`:h<24?`${h}h`:`${Math.floor(diff/86400000)}d`}
function cancelLead(leadId,btn){
if(!confirm('Cancel this lead nurture sequence? Scheduled emails will stop.')){return}
btn.disabled=true;
btn.textContent='Cancelling...';
fetch('/cancel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lead_id:leadId})})
.then(r=>r.json())
.then(data=>{
if(data.success){alert('Lead sequence cancelled successfully');loadLeads()}
else{alert('Error: '+data.error);btn.disabled=false;btn.textContent='Cancel'}
})
.catch(e=>{alert('Error: '+e.message);btn.disabled=false;btn.textContent='Cancel'})}
function renderLeads(data){
const list=document.getElementById('leads-list');
document.getElementById('active-count').textContent=data.total_leads;
document.getElementById('emails-sent').textContent=data.total_emails_sent;
document.getElementById('emails-scheduled').textContent=data.total_emails_scheduled;
if(!data.leads||data.leads.length===0){list.innerHTML='<div class="empty-state"><h3>No active leads</h3><p>Leads will appear when enrolled</p></div>';return}
list.innerHTML=data.leads.map(l=>`<div class="lead-card"><div class="lead-header"><div class="lead-info"><h3>${l.name}</h3><p>${l.email}</p></div>
<div class="lead-actions"><span class="lead-badge">${l.emails_sent_count}/5 sent</span>
<button class="cancel-btn" onclick="cancelLead('${l.lead_id}',this)">Cancel</button></div></div>
<div class="email-progress">${[1,2,3,4,5].map(n=>`<div class="email-step ${l.emails_sent.includes('email_'+n)?'sent':''}"></div>`).join('')}</div>
<div class="email-details"><div class="email-detail"><div class="label">Enrolled</div><div class="value">${formatDate(l.booked_at)}</div></div>
<div class="email-detail"><div class="label">Call Time</div><div class="value">${formatDate(l.call_time)}</div></div>
<div class="email-detail"><div class="label">Next Email</div><div class="value">${l.next_email?formatRelative(l.next_email.time):'None'}</div></div></div></div>`).join('')}
function loadLeads(){fetch('/api/leads').then(r=>r.json()).then(renderLeads).catch(e=>{document.getElementById('leads-list').innerHTML='<div class="empty-state"><h3>Error</h3><p>'+e.message+'</p></div>'})}
loadLeads();
setInterval(loadLeads,30000);
</script></body></html>"""
