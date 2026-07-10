import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft, Search, CheckCircle, AlertTriangle, Zap,
  Brain, FileText, Shield, Clock, ChevronDown, ChevronUp, ArrowRight,
} from "lucide-react";
import { getQueryDetail, QueryDetail as QueryDetailType } from "../lib/api";

const STEP_ICONS: Record<string, React.ElementType> = {
  retrieve: Search, evaluate: Brain, heal: Zap, generate: FileText,
  validate: Shield, complete: CheckCircle, failed: AlertTriangle,
};

const STEP_COLORS: Record<string, string> = {
  completed: "border-success/30 bg-success/5 text-success",
  active: "border-brand-500/30 bg-brand-500/10 text-brand-400",
  pending: "border-surface-700/50 bg-surface-800/30 text-surface-500",
  skipped: "border-surface-700/30 bg-surface-800/10 text-surface-600",
  failed: "border-danger/30 bg-danger/5 text-danger",
};

function formatDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { icon: React.ElementType; color: string }> = {
    success: { icon: CheckCircle, color: "text-success bg-success/10 border-success/20" },
    healed: { icon: Zap, color: "text-warning bg-warning/10 border-warning/20" },
    failed: { icon: AlertTriangle, color: "text-danger bg-danger/10 border-danger/20" },
    degraded: { icon: AlertTriangle, color: "text-warning bg-warning/10 border-warning/20" },
    pending: { icon: Clock, color: "text-surface-400 bg-surface-800/50 border-surface-700" },
  };
  const c = config[status] || config.pending;
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${c.color}`}>
      <Icon className="h-3.5 w-3.5" />{status}
    </span>
  );
}

function PipelineTimeline({ steps, logs }: { steps: QueryDetailType["pipeline_steps"]; logs: QueryDetailType["pipeline_logs"] }) {
  const [expandedLog, setExpandedLog] = useState<number | null>(null);
  return (
    <div className="card p-6">
      <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-surface-400 flex items-center gap-2">
        <Clock className="h-4 w-4 text-brand-400" />
        Pipeline Execution Timeline
      </h3>
      <div className="mb-8 flex items-center gap-2 flex-wrap">
        {steps.map((step, idx) => {
          const Icon = STEP_ICONS[step.step] || ArrowRight;
          const colorClass = STEP_COLORS[step.status] || STEP_COLORS.pending;
          return (
            <div key={step.step} className="flex items-center gap-2">
              <div className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-all ${colorClass}`}>
                <Icon className="h-3.5 w-3.5" />{step.label}
              </div>
              {idx < steps.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-surface-600" />}
            </div>
          );
        })}
      </div>
      <div className="space-y-1">
        {logs.map((log, idx) => {
          const Icon = STEP_ICONS[log.step] || ArrowRight;
          const isExpanded = expandedLog === idx;
          return (
            <div key={idx} className="group cursor-pointer rounded-lg border border-surface-800/50 p-3 transition-colors hover:border-surface-700 hover:bg-surface-800/20"
              onClick={() => setExpandedLog(isExpanded ? null : idx)}>
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md ${
                    log.score !== null && log.score >= 0.8 ? "bg-success/10 text-success"
                    : log.score !== null && log.score >= 0.6 ? "bg-warning/10 text-warning"
                    : "bg-surface-700/50 text-surface-400"}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm text-surface-200 group-hover:text-surface-100">{log.message}</p>
                    <p className="text-xs text-surface-500">{formatDate(log.timestamp)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {log.score !== null && (
                    <span className={`text-xs font-medium ${
                      log.score >= 0.8 ? "text-success" : log.score >= 0.6 ? "text-warning" : "text-danger"}`}>
                      {(log.score * 100).toFixed(0)}%
                    </span>
                  )}
                  {log.details && Object.keys(log.details).length > 0 && (
                    <button className="text-surface-500 hover:text-surface-300 transition-colors">
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  )}
                </div>
              </div>
              {isExpanded && log.details && (
                <div className="mt-3 ml-10 rounded-lg bg-surface-900/50 p-3">
                  <pre className="text-xs text-surface-400 overflow-x-auto">{JSON.stringify(log.details, null, 2)}</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function QueryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<QueryDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getQueryDetail(id).then((d) => { setDetail(d); setLoading(false); });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-brand-500/20 border-t-brand-500" />
          <p className="text-sm text-surface-400">Loading query details...</p>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card p-8 text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-warning mb-3" />
          <h2 className="text-lg font-semibold mb-2">Query Not Found</h2>
          <p className="text-sm text-surface-400 mb-4">The query could not be found.</p>
          <Link to="/" className="text-sm text-brand-400 hover:underline">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  const { query, pipeline_logs, pipeline_steps } = detail;

  return (
    <div className="min-h-screen bg-surface-950">
      <header className="border-b border-surface-800/60 backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-surface-400 transition-colors hover:bg-surface-800 hover:text-surface-200">
                <ArrowLeft className="h-4 w-4" />Dashboard
              </Link>
              <div className="h-5 w-px bg-surface-700" />
              <div>
                <h1 className="text-sm font-semibold text-surface-200">Query Detail</h1>
                <p className="text-xs text-surface-500 font-mono">{query.id}</p>
              </div>
            </div>
            <StatusBadge status={query.status} />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-6 animate-fade-in">
        <div className="card p-6">
          <div className="mb-4 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-surface-400">
            <Search className="h-4 w-4 text-brand-400" />User Query
          </div>
          <p className="text-lg font-medium text-surface-100 leading-relaxed">{query.query}</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-surface-800/30 p-4">
              <p className="text-xs text-surface-500 mb-1">Confidence Score</p>
              <p className={`text-2xl font-bold ${query.confidence >= 0.8 ? "text-success" : query.confidence >= 0.6 ? "text-warning" : "text-danger"}`}>
                {(query.confidence * 100).toFixed(0)}%
              </p>
            </div>
            <div className="rounded-lg bg-surface-800/30 p-4">
              <p className="text-xs text-surface-500 mb-1">Healing Actions</p>
              <p className="text-2xl font-bold text-warning">{query.healing_actions}<span className="text-sm font-normal text-surface-400 ml-1">attempts</span></p>
            </div>
            <div className="rounded-lg bg-surface-800/30 p-4">
              <p className="text-xs text-surface-500 mb-1">Processed At</p>
              <p className="text-lg font-semibold text-surface-200">{formatDate(query.created_at)}</p>
            </div>
          </div>
        </div>
        <PipelineTimeline steps={pipeline_steps} logs={pipeline_logs} />
        <div className="text-center pt-4">
          <Link to="/" className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-medium text-white transition-all hover:bg-brand-500 shadow-lg shadow-brand-500/20">
            <ArrowLeft className="h-4 w-4" />Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
