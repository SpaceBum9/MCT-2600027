/**
 * Google Workspace Real-Time Webhook Worker
 * Receives MCT Mesh Telemetry (ATM + HEARTBEAT_PHASE) and appends to the bound Sheet.
 *
 * Deploy: Extensions → Apps Script → Deploy → Web app
 *   Execute as: Me
 *   Who has access: Anyone
 * Bind this script to the spreadsheet (container-bound).
 * Optional: Script properties MCT_WEBHOOK_TOKEN — if set, body.token must match.
 * Never commit the web-app URL or the token.
 */

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonOut_({ status: "ERROR", error: "empty_body" });
    }

    var data = JSON.parse(e.postData.contents);
    var expected = PropertiesService.getScriptProperties().getProperty("MCT_WEBHOOK_TOKEN");
    if (expected) {
      var provided = (data && data.token) || (e.parameter && e.parameter.token) || "";
      if (provided !== expected) {
        return jsonOut_({ status: "ERROR", error: "unauthorized" });
      }
    }
    if (data && Object.prototype.hasOwnProperty.call(data, "token")) {
      delete data.token;
    }

    var lock = LockService.getScriptLock();
    lock.waitLock(15000);

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Timestamp", "Trace ID", "Node Source", "Phase Angle", "Status Payload"]);
      sheet.getRange(1, 1, 1, 5).setFontWeight("bold").setBackground("#f0f4f8");
    }

    var timestamp = data.utc || new Date().toISOString();
    var traceId = data.trace_id || data.watermark || "mct-trace-auto";
    var nodeSource = data.node || "ALG_0_EGELHEIMER";
    var phaseAngle = data.phase_angle;
    if (phaseAngle === undefined || phaseAngle === null) {
      phaseAngle = data.phase_vector !== undefined ? data.phase_vector : "0.0";
    }

    sheet.appendRow([timestamp, traceId, nodeSource, phaseAngle, JSON.stringify(data)]);
    lock.releaseLock();

    return jsonOut_({
      status: "SUCCESS",
      message: "Telemetry written to Google Workspace",
      timestamp: timestamp,
      trace_id: traceId
    });
  } catch (error) {
    return jsonOut_({ status: "ERROR", error: error.toString() });
  }
}

function doGet() {
  return ContentService.createTextOutput(
    "MCT Google Space Worker Online. Send POST requests to dispatch telemetry."
  );
}

function jsonOut_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
