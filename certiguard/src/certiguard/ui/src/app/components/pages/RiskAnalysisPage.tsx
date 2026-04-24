import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const globalRiskTrend = [
  { date: "Apr 18", score: 28 },
  { date: "Apr 19", score: 32 },
  { date: "Apr 20", score: 41 },
  { date: "Apr 21", score: 38 },
  { date: "Apr 22", score: 45 },
  { date: "Apr 23", score: 52 },
  { date: "Apr 24", score: 47 },
];

const threatCategories = [
  { category: "Tampering", count: 34 },
  { category: "VM Cloning", count: 18 },
  { category: "Debugger", count: 22 },
  { category: "Hardware", count: 12 },
  { category: "Anomaly", count: 28 },
];

const aiInsights = [
  {
    id: 1,
    title: "Coordinated Attack Pattern Detected",
    description: "3 clients with similar tampering signatures within 24 hours, suggesting coordinated reverse engineering attempt.",
    affected: 3,
    confidence: 94,
  },
  {
    id: 2,
    title: "Unusual Activity Spike on Weekends",
    description: "Statistical analysis shows 3.2σ deviation in weekend usage patterns, indicating potential unauthorized access.",
    affected: 7,
    confidence: 87,
  },
  {
    id: 3,
    title: "License Expiry Manipulation Risk",
    description: "82% probability of expiration date tampering attempts in clients approaching renewal deadline.",
    affected: 12,
    confidence: 82,
  },
];

export function RiskAnalysisPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Risk Analysis</h1>
        <p className="mt-0.5 text-sm text-gray-500">AI-powered threat intelligence and behavioral analysis</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Global Risk Score</div>
          <div className="text-3xl font-semibold">47</div>
          <div className="mt-2 text-xs text-emerald-400">AI Powered</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Total Threats (7d)</div>
          <div className="text-3xl font-semibold">114</div>
          <div className="mt-2 text-xs text-gray-400">Detected events</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Detection Accuracy</div>
          <div className="text-3xl font-semibold">98.2%</div>
          <div className="mt-2 text-xs text-gray-400">ML model performance</div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Monitored Clients</div>
          <div className="text-3xl font-semibold">1,247</div>
          <div className="mt-2 text-xs text-gray-400">Active licenses</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Global Risk Trend</h3>
            <p className="mt-0.5 text-xs text-gray-500">Aggregate security risk over time</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={globalRiskTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1117",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              />
              <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Threat Categories</h3>
            <p className="mt-0.5 text-xs text-gray-500">Distribution by attack vector (7 days)</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={threatCategories} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis type="number" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis dataKey="category" type="category" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} width={80} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1117",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[0, 2, 2, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded border border-white/5 bg-[#0d1117] p-5">
        <div className="mb-5">
          <h3 className="text-sm font-medium">AI-Generated Insights</h3>
          <p className="mt-0.5 text-xs text-gray-500">Machine learning threat intelligence</p>
        </div>
        <div className="space-y-3">
          {aiInsights.map((insight) => (
            <div
              key={insight.id}
              className="rounded border border-white/5 bg-white/[0.02] p-4"
            >
              <div className="mb-2 flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium">{insight.title}</h4>
                  <p className="mt-1 text-sm text-gray-400">{insight.description}</p>
                </div>
                <div className="ml-4 text-right">
                  <div className="text-2xl font-semibold text-emerald-400">{insight.confidence}%</div>
                  <div className="text-xs text-gray-500">Confidence</div>
                </div>
              </div>
              <div className="mt-3 border-t border-white/5 pt-3 text-xs text-gray-400">
                <span className="font-medium text-emerald-400">{insight.affected}</span> affected clients
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
