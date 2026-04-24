import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { useState, useEffect } from "react";

const usageData = [
  { time: "00:00", activity: 120 },
  { time: "04:00", activity: 89 },
  { time: "08:00", activity: 245 },
  { time: "12:00", activity: 389 },
  { time: "16:00", activity: 421 },
  { time: "20:00", activity: 298 },
];

const threatData = [
  { hour: "00", count: 12 },
  { hour: "04", count: 8 },
  { hour: "08", count: 34 },
  { hour: "12", count: 56 },
  { hour: "16", count: 67 },
  { hour: "20", count: 43 },
];

const securityEvents = [
  { id: 1, message: "License tampering detected", client: "Client-8F3A", severity: "critical", time: "2s ago" },
  { id: 2, message: "VM clone attempt blocked", client: "Client-B921", severity: "high", time: "8s ago" },
  { id: 3, message: "Debugger detected on client", client: "Client-C4E7", severity: "medium", time: "23s ago" },
  { id: 4, message: "Anomaly score increased to 87", client: "Client-2D91", severity: "high", time: "41s ago" },
  { id: 5, message: "Hardware mismatch detected", client: "Client-F612", severity: "critical", time: "1m ago" },
];

export function OverviewPage() {
  const [liveEvents, setLiveEvents] = useState(securityEvents);

  useEffect(() => {
    const interval = setInterval(() => {
      const newEvent = {
        id: Date.now(),
        message: [
          "License verification failed",
          "Suspicious activity detected",
          "Boot counter anomaly",
          "Hash chain validation error",
        ][Math.floor(Math.random() * 4)],
        client: `Client-${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
        severity: ["critical", "high", "medium"][Math.floor(Math.random() * 3)] as "critical" | "high" | "medium",
        time: "just now",
      };
      setLiveEvents((prev) => [newEvent, ...prev.slice(0, 4)]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="mt-0.5 text-sm text-gray-500">Real-time license protection and threat monitoring</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Active Licenses</div>
          <div className="text-3xl font-semibold">1,247</div>
          <div className="mt-2 text-xs text-emerald-400">+12.5% vs last week</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Blacklisted</div>
          <div className="text-3xl font-semibold">23</div>
          <div className="mt-2 text-xs text-red-400">+3 new</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Security Events</div>
          <div className="text-3xl font-semibold">8,941</div>
          <div className="mt-2 text-xs text-gray-400">Last 7 days</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">High-Risk Clients</div>
          <div className="text-3xl font-semibold">47</div>
          <div className="mt-2 text-xs text-orange-400">Requires attention</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Client Activity</h3>
            <p className="mt-0.5 text-xs text-gray-500">Last 24 hours</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1117",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              />
              <Line type="monotone" dataKey="activity" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Status Distribution</h3>
            <p className="mt-0.5 text-xs text-gray-500">Current state</p>
          </div>
          <div className="space-y-4">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-gray-400">Safe</span>
                <span className="font-medium">1,177</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full w-[94%] bg-emerald-500" />
              </div>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-gray-400">Suspicious</span>
                <span className="font-medium">47</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full w-[4%] bg-orange-500" />
              </div>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-gray-400">Blacklisted</span>
                <span className="font-medium">23</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full w-[2%] bg-red-500" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">Security Events</h3>
              <p className="mt-0.5 text-xs text-gray-500">Real-time threat feed</p>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
              <span className="text-xs text-gray-400">Live</span>
            </div>
          </div>
          <div className="space-y-2">
            {liveEvents.map((event) => (
              <div
                key={event.id}
                className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3 transition-colors hover:bg-white/5"
              >
                <div className="flex-1">
                  <div className="text-sm">{event.message}</div>
                  <div className="mt-0.5 text-xs text-gray-500">{event.client}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`rounded px-2 py-0.5 text-xs font-medium ${
                    event.severity === "critical" ? "bg-red-500/10 text-red-400" :
                    event.severity === "high" ? "bg-orange-500/10 text-orange-400" :
                    "bg-yellow-500/10 text-yellow-400"
                  }`}>
                    {event.severity}
                  </span>
                  <span className="text-xs text-gray-500">{event.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Threat Activity</h3>
            <p className="mt-0.5 text-xs text-gray-500">Events by hour</p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={threatData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="hour" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1117",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
