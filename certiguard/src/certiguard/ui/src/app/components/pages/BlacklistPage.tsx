const blacklistedClients = [
  {
    id: "8F3A",
    name: "Acme Corporation",
    license: "LIC-8F3A-9B2C",
    reason: "Repeated license tampering attempts",
    events: 12,
    date: "2026-04-23",
  },
  {
    id: "D4B7",
    name: "ShadowTech Ltd",
    license: "LIC-D4B7-3E9A",
    reason: "License cloning detected across multiple instances",
    events: 8,
    date: "2026-04-22",
  },
  {
    id: "E2C9",
    name: "ByteHack Solutions",
    license: "LIC-E2C9-7F1B",
    reason: "Persistent debugger and reverse engineering attempts",
    events: 15,
    date: "2026-04-20",
  },
  {
    id: "A8F3",
    name: "DataBreak Inc",
    license: "LIC-A8F3-2D6C",
    reason: "Abnormal usage behavior - suspicious concurrent sessions",
    events: 6,
    date: "2026-04-21",
  },
];

export function BlacklistPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Blacklist</h1>
          <p className="mt-0.5 text-sm text-gray-500">Blocked clients and enforcement actions</p>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] px-4 py-2">
          <div className="text-2xl font-semibold text-red-400">{blacklistedClients.length}</div>
          <div className="text-xs text-gray-500">Blocked</div>
        </div>
      </div>

      <div className="space-y-3">
        {blacklistedClients.map((client) => (
          <div
            key={client.id}
            className="rounded border border-white/5 bg-[#0d1117] p-5 transition-colors hover:border-red-500/20"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="mb-3 flex items-center gap-3">
                  <h3 className="font-medium">{client.name}</h3>
                  <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-400">
                    Blacklisted
                  </span>
                </div>
                <code className="text-sm text-gray-400">{client.license}</code>
                <div className="mt-3 text-sm text-gray-300">{client.reason}</div>
                <div className="mt-3 flex gap-6 text-sm">
                  <div>
                    <span className="text-gray-500">Events:</span>{" "}
                    <span className="font-medium text-red-400">{client.events}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Blacklisted:</span>{" "}
                    <span className="text-gray-300">{client.date}</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="rounded border border-white/5 bg-white/5 px-3 py-1.5 text-sm text-gray-300 transition-colors hover:bg-white/10">
                  Review
                </button>
                <button className="rounded border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-sm text-emerald-400 transition-colors hover:bg-emerald-500/20">
                  Reinstate
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
