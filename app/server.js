const appInsights = require("applicationinsights");

// Initialize Application Insights if connection string is set
if (process.env.APPLICATIONINSIGHTS_CONNECTION_STRING) {
  appInsights.setup(process.env.APPLICATIONINSIGHTS_CONNECTION_STRING)
    .setAutoCollectRequests(true)
    .setAutoCollectPerformance(true)
    .setAutoCollectExceptions(true)
    .setAutoCollectDependencies(true)
    .setAutoCollectConsole(true, true)
    .setSendLiveMetrics(true)
    .start();
}

const path = require("path");
const express = require("express");
const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// ---------- helpers ----------

function isHealthy() {
  return (process.env.APP_HEALTHY || "true").toLowerCase() === "true";
}

// Simulate CPU burn when unhealthy (makes response times spike)
function simulateCpuLoad(durationMs) {
  const end = Date.now() + durationMs;
  while (Date.now() < end) {
    Math.sqrt(Math.random() * 999999);
  }
}

// ---------- routes ----------

// Landing page — serve the dashboard HTML
app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Health probe (App Service uses this)
app.get("/health", (_req, res) => {
  if (isHealthy()) {
    return res.status(200).json({ status: "healthy", timestamp: new Date().toISOString() });
  }

  // Log to Application Insights
  if (appInsights.defaultClient) {
    appInsights.defaultClient.trackException({
      exception: new Error("Health check failed - service degraded"),
      severity: appInsights.Contracts.SeverityLevel.Critical,
      properties: { component: "health-probe" },
    });
  }

  return res.status(503).json({ status: "unhealthy", timestamp: new Date().toISOString(), error: "Service degraded" });
});

// Application status with details
app.get("/api/status", (_req, res) => {
  const healthy = isHealthy();
  const uptime = process.uptime();

  if (!healthy) {
    simulateCpuLoad(200); // add latency
  }

  res.status(200).json({
    healthy,
    uptime: `${Math.floor(uptime)}s`,
    memoryUsage: process.memoryUsage(),
    nodeVersion: process.version,
    environment: process.env.NODE_ENV || "production",
    timestamp: new Date().toISOString(),
  });
});

// Simulate document processing
app.post("/api/process", (req, res) => {
  const { documentType, fileName } = req.body || {};

  if (!isHealthy()) {
    simulateCpuLoad(500); // heavy latency when broken

    const error = new Error("Document processing engine failure - connection pool exhausted");
    if (appInsights.defaultClient) {
      appInsights.defaultClient.trackException({
        exception: error,
        severity: appInsights.Contracts.SeverityLevel.Error,
        properties: {
          component: "document-processor",
          documentType: documentType || "unknown",
          fileName: fileName || "unknown",
        },
      });
      appInsights.defaultClient.trackEvent({
        name: "DocumentProcessingFailed",
        properties: { reason: "engine_failure", documentType: documentType || "unknown" },
      });
    }

    return res.status(500).json({
      error: "Internal Server Error",
      message: "Document processing engine failure - connection pool exhausted",
      correlationId: `err-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp: new Date().toISOString(),
    });
  }

  // Simulate processing time (100-400ms)
  const processingTime = 100 + Math.floor(Math.random() * 300);
  setTimeout(() => {
    const docId = `doc-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    if (appInsights.defaultClient) {
      appInsights.defaultClient.trackEvent({
        name: "DocumentProcessed",
        properties: { documentType: documentType || "invoice", fileName: fileName || "unnamed" },
        measurements: { processingTimeMs: processingTime },
      });
    }

    res.status(200).json({
      documentId: docId,
      status: "processed",
      documentType: documentType || "invoice",
      fileName: fileName || "unnamed",
      processingTimeMs: processingTime,
      extractedFields: {
        vendor: "Contoso Ltd.",
        amount: (Math.random() * 10000).toFixed(2),
        currency: "EUR",
        date: new Date().toISOString().split("T")[0],
        confidence: (0.85 + Math.random() * 0.14).toFixed(2),
      },
      timestamp: new Date().toISOString(),
    });
  }, processingTime);
});

// List documents (mock)
app.get("/api/documents", (_req, res) => {
  if (!isHealthy()) {
    simulateCpuLoad(300);
  }

  const docs = Array.from({ length: 5 }, (_, i) => ({
    documentId: `doc-sample-${i + 1}`,
    fileName: `invoice-${2024 + i}.pdf`,
    documentType: "invoice",
    status: isHealthy() ? "processed" : "failed",
    processedAt: new Date(Date.now() - i * 3600000).toISOString(),
  }));

  res.status(200).json({ documents: docs, total: docs.length });
});

// Get single document (mock)
app.get("/api/documents/:id", (req, res) => {
  if (!isHealthy()) {
    simulateCpuLoad(200);
    if (appInsights.defaultClient) {
      appInsights.defaultClient.trackException({
        exception: new Error(`Failed to retrieve document ${req.params.id} - storage timeout`),
        severity: appInsights.Contracts.SeverityLevel.Error,
        properties: { component: "document-store", documentId: req.params.id },
      });
    }
    return res.status(500).json({ error: "Storage timeout", documentId: req.params.id });
  }

  res.status(200).json({
    documentId: req.params.id,
    fileName: "invoice-2024.pdf",
    documentType: "invoice",
    status: "processed",
    extractedFields: {
      vendor: "Contoso Ltd.",
      amount: "4250.00",
      currency: "EUR",
      date: "2024-11-15",
      confidence: "0.97",
    },
    processedAt: new Date().toISOString(),
  });
});

// ---------- start ----------

app.listen(PORT, () => {
  console.log(`SRE Demo App listening on port ${PORT}`);
  console.log(`APP_HEALTHY = ${isHealthy()}`);
});
