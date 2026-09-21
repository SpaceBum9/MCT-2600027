/**
 * SoS GPT Delta Wake relay.
 * Deploy behind HTTPS (for example as an edge/serverless function).
 * Required env/secrets:
 *   INBOUND_TOKEN   GitHub -> relay bearer token
 *   PUSH_URL        downstream iOS push/automation endpoint
 *   PUSH_TOKEN      optional downstream bearer token
 *
 * The relay carries references only. It grants no merge/execute/payment authority.
 */
export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("method not allowed", { status: 405 });

    const auth = request.headers.get("authorization") || "";
    if (!env.INBOUND_TOKEN || auth !== `Bearer ${env.INBOUND_TOKEN}`) {
      return new Response("unauthorized", { status: 401 });
    }

    let p;
    try { p = await request.json(); }
    catch { return new Response("invalid json", { status: 400 }); }

    if (p?.schema !== "sos.gpt-wake.v1" || p?.to !== "GPT" ||
        typeof p?.repo !== "string" || typeof p?.sha !== "string" ||
        typeof p?.delivery_id !== "string") {
      return new Response("invalid packet", { status: 422 });
    }
    if (!env.PUSH_URL) return new Response("push transport not configured", { status: 503 });

    const message = {
      title: "SoS GitHub Delta",
      body: `${p.repo} · ${p.event} · ${p.sha.slice(0, 12)}`,
      payload: p,
      shortcut: "SoS GPT Delta Wake"
    };

    const headers = { "content-type": "application/json" };
    if (env.PUSH_TOKEN) headers.authorization = `Bearer ${env.PUSH_TOKEN}`;

    const r = await fetch(env.PUSH_URL, {
      method: "POST",
      headers,
      body: JSON.stringify(message)
    });

    if (!r.ok) return new Response("downstream push failed", { status: 502 });
    return new Response(JSON.stringify({ ok: true, delivery_id: p.delivery_id }), {
      status: 202, headers: { "content-type": "application/json" }
    });
  }
};
