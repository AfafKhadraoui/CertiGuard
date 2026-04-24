import { Link } from "react-router";

const clients = [
  { id: "8F3A", name: "Acme Corporation", license: "LIC-8F3A-9B2C", status: "blacklisted", risk: 95, lastActivity: "2m ago", users: 50 },
  { id: "B921", name: "TechVault Inc", license: "LIC-B921-4E7D", status: "suspicious", risk: 72, lastActivity: "5m ago", users: 120 },
  { id: "C4E7", name: "DataSync LLC", license: "LIC-C4E7-1A8F", status: "safe", risk: 12, lastActivity: "1h ago", users: 75 },
  { id: "2D91", name: "CloudCore Systems", license: "LIC-2D91-6C3B", status: "suspicious", risk: 68, lastActivity: "12m ago", users: 200 },
  { id: "F612", name: "SecureNet Global", license: "LIC-F612-9D4A", status: "safe", risk: 8, lastActivity: "45m ago", users: 90 },
  { id: "A5C3", name: "IntegraSoft", license: "LIC-A5C3-2F8E", status: "safe", risk: 15, lastActivity: "2h ago", users: 35 },
  { id: "7B9E", name: "NexGen Analytics", license: "LIC-7B9E-5C1D", status: "suspicious", risk: 64, lastActivity: "8m ago", users: 150 },
  { id: "3E1F", name: "ByteForge Labs", license: "LIC-3E1F-8A6B", status: "safe", risk: 5, lastActivity: "3h ago", users: 60 },
];

export function ClientsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Clients</h1>
        <p className="mt-0.5 text-sm text-gray-500">Monitor and manage licensed clients</p>
      </div>

      <div className="rounded border border-white/5 bg-[#0d1117] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Client</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">License</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Risk</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Users</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Last Activity</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {clients.map((client) => (
              <tr
                key={client.id}
                className="group transition-colors hover:bg-white/[0.02]"
              >
                <td className="px-4 py-3">
                  <div>
                    <div className="text-sm font-medium">{client.name}</div>
                    <div className="text-xs text-gray-500">Client-{client.id}</div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <code className="text-xs text-gray-400">{client.license}</code>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-xs ${
                    client.status === "blacklisted" ? "bg-red-500/10 text-red-400" :
                    client.status === "suspicious" ? "bg-orange-500/10 text-orange-400" :
                    "bg-emerald-500/10 text-emerald-400"
                  }`}>
                    <div className={`h-1 w-1 rounded-full ${
                      client.status === "blacklisted" ? "bg-red-400" :
                      client.status === "suspicious" ? "bg-orange-400" :
                      "bg-emerald-400"
                    }`} />
                    {client.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1 w-16 overflow-hidden rounded-full bg-white/5">
                      <div
                        className={`h-full ${
                          client.risk >= 70 ? "bg-red-500" :
                          client.risk >= 40 ? "bg-orange-500" :
                          "bg-emerald-500"
                        }`}
                        style={{ width: `${client.risk}%` }}
                      />
                    </div>
                    <span className={`text-xs ${
                      client.risk >= 70 ? "text-red-400" :
                      client.risk >= 40 ? "text-orange-400" :
                      "text-emerald-400"
                    }`}>
                      {client.risk}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{client.users}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{client.lastActivity}</td>
                <td className="px-4 py-3">
                  <Link
                    to={`/clients/${client.id}`}
                    className="text-sm text-emerald-400 opacity-0 transition-opacity group-hover:opacity-100 hover:text-emerald-300"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
