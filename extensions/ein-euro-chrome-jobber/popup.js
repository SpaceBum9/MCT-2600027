function $(id) {
  return document.getElementById(id);
}

function setStatus(text, ok) {
  const el = $("status");
  el.textContent = text || "";
  el.style.color = ok ? "#065f46" : "#b91c1c";
}

function render(data) {
  const routes = $("routes");
  routes.replaceChildren();
  (data.routes || []).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r.host + " → " + r.template;
    routes.appendChild(li);
  });
  const jobs = $("jobs");
  jobs.replaceChildren();
  (data.jobs || []).forEach((j) => {
    const li = document.createElement("li");
    li.textContent = j.utc + " · " + j.host + " · " + j.id;
    jobs.appendChild(li);
  });
}

function send(type, extra) {
  return chrome.runtime.sendMessage({ type, ...(extra || {}) });
}

async function refresh() {
  const data = await send("LIST");
  render(data);
}

$("save").addEventListener("click", async () => {
  const res = await send("SAVE_ROUTE", {
    host: $("host").value,
    template: $("template").value,
  });
  if (!res.ok) {
    setStatus(res.error, false);
    return;
  }
  setStatus("Route gespeichert. Nur mit Partnervertrag nutzen.", true);
  render(res);
});

$("job").addEventListener("click", async () => {
  const res = await send("JOB_ACTIVE_TAB");
  if (!res.ok) {
    setStatus(res.error + (res.hint ? " — " + res.hint : ""), false);
    return;
  }
  setStatus("Job " + res.job.id + " · Nutzerklick", true);
  await refresh();
});

refresh();
