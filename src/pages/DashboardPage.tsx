import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell,
} from "recharts";
import {
  Activity, Brain, Shield, AlertTriangle, Zap, RefreshCw,
  Search, CheckCircle, FileText, Clock, ArrowRight, TrendingUp,
} from "lucide-react";
import { getDashboardData, DashboardData } from "../lib/api";

const PIE_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6"];
const STATUS_COLORS: Record<string, string> = {
  success: "text-success bg-success/10 border-success/20",
  healed: "text-warning bg-warning/10 border-warning/20",
  failed: "text-danger bg-danger/10 border-danger/20",
  degraded: "text-warning bg-warning/10 border-warning/20",
};

function formatDate(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function Header() {
  return (
    <header className="border-b border-surface-800/60 backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 shadow-lg shadow-brand-500/20">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                <span className="gradient-text">Self-Healing</span> RAG Pipeline
              </h1>
              <p className="text-xs text-surface-500">Observability Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 rounded-full bg-success/10 px-3 py-1.5 text-xs text-success">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
              Pipeline Active
            </div>
            <button className="rounded-lg border border-surface-700 bg-surface-800 p-2 text-surface-400 transition-colors hover:border-surface-600 hover:text-surface-200">
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function StatCard({ title, value, sub, icon: Icon, color }: {
  title: string; value: string | number; sub?: string; icon: React.ElementType; color: string;
}) {
  return (
    <div className="group card-hover p-5">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="stat-label">{title}</p>
          <p className="stat-value gradient-text">{value}</p>
          {sub && <p className="text-xs text-surface-500">{sub}</p>}
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color} transition-transform group-hover:scale-110`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function ChartCard({ title, icon: Icon, children }: {
  title: string; icon: React.ElementType; children: React.ReactNode;
}) {
  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center gap-2 text-sm font-medium text-surface-300">
        <Icon className="h-4 w-4 text-brand-400" />
        {title}
      </div>
      {children}
    </div>
  );
}

function ActivityTable({ queries }: { queries: DashboardData["recent_queries"] }) {
  if (!queries.length) {
    return (
      <div className="card p-8 text-center">
        <FileText className="mx-auto h-8 w-8 text-surface-600 mb-3" />
        <p className="text-surface-400 text-sm">No queries processed yet</p>
      </div>
    );
  }
  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-800">
              <th className="px-4 py-3 text-left font-medium text-surface-400">Query</th>
              <th className="px-4 py-3 text-left font-medium text-surface-400">Status</th>
              <th className="px-4 py-3 text-left font-medium text-surface-400">Confidence</th>
              <th className="px-4 py-3 text-left font-medium text-surface-400">Healing</th>
              <th className="px-4 py-3 text-left font-medium text-surface-400">Time</th>
              <th className="px-4 py-3 text-right font-medium text-surface-400">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-800/50">
            {queries.map((q) => (
              <tr key={q.id} className="group transition-colors hover:bg-surface-800/30">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Search className="h-3.5 w-3.5 shrink-0 text-surface-500" />
                    <span className="truncate max-w-[300px] text-surface-200">{q.query}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border ${STATUS_COLORS[q.status] || "text-surface-400 bg-surface-800/50"}`}>
                    {q.status === "success" && <CheckCircle className="h-3 w-3" />}
                    {q.status === "healed" && <Zap className="h-3 w-3" />}
                    {q.status === "failed" && <AlertTriangle className="h-3 w-3" />}
                    {q.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-700">
                      <div className={`h-full rounded-full transition-all ${
                        q.confidence >= 0.8 ? "bg-success" : q.confidence >= 0.6 ? "bg-warning" : "bg-danger"
                      }`} style={{ width: `${q.confidence * 100}%` }} />
                    </div>
                    <span className="text-xs text-surface-400">{(q.confidence * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-surface-400">
                  {q.healing_actions > 0 ? (
                    <span className="text-warning">{q.healing_actions}x</span>
                  ) : (
                    <span className="text-surface-500">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-xs text-surface-500">{formatDate(q.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <Link
                    to={`/queries/${q.id}`}
                    className="inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs font-medium text-brand-400 transition-colors hover:bg-brand-500/10"
                  >
                    Details <ArrowRight className="h-3 w-3" />
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

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardData().then((d) => { setData(d); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-brand-500/20 border-t-brand-500" />
          <p className="text-sm text-surface-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card p-8 text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-warning mb-3" />
          <h2 className="text-lg font-semibold mb-2">Failed to load dashboard</h2>
          <p className="text-sm text-surface-400">Check that the backend API is running.</p>
        </div>
      </div>
    );
  }

  const { summary, queries_over_time, confidence_distribution, healing_distribution, recent_queries } = data;

  return (
    <div className="min-h-screen bg-surface-950">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 animate-fade-in">
        {/* Stats Grid */}
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand-400" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-surface-400">Pipeline Overview</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard title="Total Queries" value={summary.total_queries} sub="Processed this week" icon={Activity} color="bg-brand-500/10 text-brand-400" />
            <StatCard title="Avg Confidence" value={`${(summary.avg_confidence * 100).toFixed(0)}%`} sub="Score across all queries" icon={Shield} color="bg-success/10 text-success" />
            <StatCard title="Avg Healing Iterations" value={summary.avg_healing_iterations.toFixed(1)} sub="Per query" icon={RefreshCw} color="bg-warning/10 text-warning" />
            <StatCard title="Error Rate" value={`${summary.error_rate}%`} sub="Of total queries" icon={AlertTriangle} color="bg-danger/10 text-danger" />
          </div>
        </section>

        {/* Charts */}
        <section className="grid gap-6 lg:grid-cols-3">
          <ChartCard title="Queries Over Time" icon={TrendingUp}>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={queries_over_time}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "rgba(30,41,59,0.95)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: "8px", fontSize: "12px" }} />
                <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2.5} dot={{ fill: "#6366f1", strokeWidth: 0, r: 4 }} activeDot={{ r: 6, fill: "#818cf8" }} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Confidence Distribution" icon={Shield}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={confidence_distribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "rgba(30,41,59,0.95)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {confidence_distribution.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Healing Actions Distribution" icon={Zap}>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={healing_distribution} dataKey="count" nameKey="action" cx="50%" cy="50%" outerRadius={80}
                  label={({ action, percent }) => `${action} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: "#475569", strokeWidth: 1 }}>
                  {healing_distribution.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "rgba(30,41,59,0.95)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: "8px", fontSize: "12px" }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </section>

        {/* Success Breakdown */}
        <section className="grid gap-4 sm:grid-cols-3">
          {[
            { label: "Success Rate", value: `${summary.success_rate}%`, color: "from-success to-emerald-600", icon: CheckCircle },
            { label: "Healed Rate", value: `${summary.healed_rate}%`, color: "from-warning to-amber-600", icon: Zap },
            { label: "Failure Rate", value: `${summary.error_rate}%`, color: "from-danger to-rose-600", icon: AlertTriangle },
          ].map((item) => (
            <div key={item.label} className="card relative overflow-hidden p-5">
              <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-5`} />
              <div className="relative flex items-center gap-4">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} shadow-lg`}>
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="stat-label">{item.label}</p>
                  <p className="stat-value gradient-text">{item.value}</p>
                </div>
              </div>
            </div>
          ))}
        </section>

        {/* Recent Activity */}
        <section>
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-brand-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-surface-400">Recent Activity</h2>
            </div>
            <span className="text-xs text-surface-500">{recent_queries.length} latest queries</span>
          </div>
          <ActivityTable queries={recent_queries} />
        </section>
      </main>
    </div>
  );
}
