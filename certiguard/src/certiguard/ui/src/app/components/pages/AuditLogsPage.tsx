const auditLogs = [
  {
    id: 1,
    timestamp: "2026-04-24 14:32:15",
    event: "License signature verification failed - Ed25519 signature mismatch",
    client: "Client-8F3A",
    license: "LIC-8F3A-9B2C",
    severity: "critical",
    hash: "a7b3c9d2e4f1a8b6c3d9e2f4a1b8c5d7e3f9a2b4c6d8e1f3a5b7c9d2e4f6a8b1",
  },
  {
    id: 2,
    timestamp: "2026-04-24 14:28:42",
    event: "Virtual machine clone detected via boot counter regression",
    client: "Client-B921",
    license: "LIC-B921-4E7D",
    severity: "high",
    hash: "b8c4d1e5f2a9b7c4d1e6f3a2b9c6d8e4f1a7b3c5d2e9f4a6b8c1d7e3f5a9b2c4",
  },
  {
    id: 3,
    timestamp: "2026-04-24 14:15:23",
    event: "Debugger attachment attempt detected and blocked",
    client: "Client-C4E7",
    license: "LIC-C4E7-1A8F",
    severity: "medium",
    hash: "c9d5e2f6a3b1c8d4e1f7a4b2c9d6e3f1a8b5c2d9e6f3a1b7c4d2e8f5a3b9c6d1",
  },
  {
    id: 4,
    timestamp: "2026-04-24 13:58:07",
    event: "AI anomaly detection: usage pattern deviation σ=3.2 from baseline",
    client: "Client-2D91",
    license: "LIC-2D91-6C3B",
    severity: "high",
    hash: "d1e6f3a4b2c9d5e2f8a5b3c1d7e4f1a9b6c3d2e8f5a2b9c6d4e1f7a3b5c8d2e6",
  },
  {
    id: 5,
    timestamp: "2026-04-24 13:42:31",
    event: "Hardware fingerprint mismatch - CPU signature validation failed",
    client: "Client-F612",
    license: "LIC-F612-9D4A",
    severity: "critical",
    hash: "e2f7a5b3c1d8e4f2a9b6c4d1e7f3a2b8c5d9e6f4a1b7c3d2e9f5a4b1c6d8e3f7",
  },
];

export function AuditLogsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Audit Logs</h1>
          <p className="mt-0.5 text-sm text-gray-500">Tamper-evident hash-chained security events</p>
        </div>
        <button className="rounded border border-white/5 bg-white/5 px-3 py-1.5 text-sm text-gray-300 transition-colors hover:bg-white/10">
          Export Logs
        </button>
      </div>

      <div className="rounded border border-white/5 bg-[#0d1117]">
        <div className="border-b border-white/5 px-4 py-2.5">
          <div className="flex items-center gap-2 text-xs">
            <div className="h-1 w-1 rounded-full bg-emerald-500" />
            <span className="text-emerald-400">Hash Chain Integrity: VERIFIED</span>
          </div>
        </div>

        <div className="divide-y divide-white/5">
          {auditLogs.map((log) => (
            <div key={log.id} className="p-5">
              <div className="mb-2 flex items-center gap-3">
                <span className={`rounded px-2 py-0.5 text-xs font-medium ${
                  log.severity === "critical" ? "bg-red-500/10 text-red-400" :
                  log.severity === "high" ? "bg-orange-500/10 text-orange-400" :
                  "bg-yellow-500/10 text-yellow-400"
                }`}>
                  {log.severity}
                </span>
                <span className="text-xs text-gray-500">{log.timestamp}</span>
              </div>
              <div className="mb-2 text-sm">{log.event}</div>
              <div className="mb-3 flex gap-4 text-xs">
                <div>
                  <span className="text-gray-500">Client:</span>{" "}
                  <span className="text-gray-400">{log.client}</span>
                </div>
                <div>
                  <span className="text-gray-500">License:</span>{" "}
                  <code className="text-gray-400">{log.license}</code>
                </div>
              </div>
              <div className="rounded border border-white/5 bg-white/[0.02] p-2.5">
                <div className="mb-1 text-xs text-gray-500">Hash Chain Link</div>
                <code className="break-all text-xs text-gray-400">{log.hash}</code>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
