/* Ein-Euro Chrome-Jobber — no declarativeNetRequest, no <all_urls>. */

const DEFAULT_STATE = {
  routes: [],
  jobs: [],
};

function utcNow() {
  return new Date().toISOString();
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function matchRoute(routes, url) {
  const host = hostOf(url);
  return (routes || []).find((r) => host === r.host || host.endsWith("." + r.host));
}

function applyTemplate(template, tabUrl) {
  const u = new URL(tabUrl);
  return template
    .replaceAll("{url}", encodeURIComponent(tabUrl))
    .replaceAll("{host}", u.hostname)
    .replaceAll("{path}", u.pathname + u.search);
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  const run = async () => {
    const state = await chrome.storage.local.get(DEFAULT_STATE);
    const routes = state.routes || [];
    const jobs = state.jobs || [];

    if (msg.type === "LIST") {
      return { routes, jobs: jobs.slice(-20).reverse() };
    }

    if (msg.type === "SAVE_ROUTE") {
      const host = String(msg.host || "").trim().replace(/^www\./, "");
      const template = String(msg.template || "").trim();
      if (!host || !template) return { ok: false, error: "host_and_template_required" };
      if (!/^https:\/\//i.test(template) && !template.includes("{url}")) {
        return { ok: false, error: "https_template_required" };
      }
      const next = routes.filter((r) => r.host !== host);
      next.push({
        host,
        template,
        disclosure: "affiliate",
        agreement: true,
      });
      await chrome.storage.local.set({ routes: next });
      return { ok: true, routes: next };
    }

    if (msg.type === "JOB_ACTIVE_TAB") {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.url || !tab.id) return { ok: false, error: "no_active_tab" };
      if (!tab.url.startsWith("https://")) return { ok: false, error: "https_only" };

      const route = matchRoute(routes, tab.url);
      if (!route) {
        return {
          ok: false,
          error: "no_route",
          host: hostOf(tab.url),
          hint: "Nur Händler mit deinem eigenen Partnervertrag.",
        };
      }

      const target = applyTemplate(route.template, tab.url);
      const job = {
        id: "job_" + Date.now().toString(36),
        utc: utcNow(),
        source: tab.url,
        target,
        host: route.host,
        node: "EIN_EURO_JOBBER",
        payload_type: "AFFILIATE_ROUTE",
        user_gesture: true,
        claims_external_delivery: false,
      };
      jobs.push(job);
      await chrome.storage.local.set({ jobs: jobs.slice(-100) });
      await chrome.tabs.update(tab.id, { url: target });
      return { ok: true, job };
    }

    return { ok: false, error: "unknown" };
  };

  run().then(sendResponse).catch((err) => sendResponse({ ok: false, error: String(err) }));
  return true;
});
