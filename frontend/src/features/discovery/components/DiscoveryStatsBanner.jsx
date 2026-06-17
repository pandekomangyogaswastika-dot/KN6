/** DiscoveryStatsBanner — 4-card KPI banner above the session list. */
import { Card } from "@/components/ui/card";
import { BellRing, Inbox, ClipboardCheck, FileText } from "lucide-react";
import { formatRelative } from "./discoveryFormat";

export const DiscoveryStatsBanner = ({ stats }) => {
  if (!stats) return null;
  return (
    <div className="mb-6 grid gap-3 sm:grid-cols-4" data-testid="admin-stats-banner">
      <Card className={`border-discovery-border bg-white p-4 ${stats.new_submissions > 0 ? "ring-2 ring-discovery-warn/40" : ""}`}>
        <div className="flex items-center gap-2 text-xs text-discovery-muted">
          <BellRing size={13} className={stats.new_submissions > 0 ? "text-discovery-warn" : ""} />
          Submission Baru
        </div>
        <p
          className={`mt-1 text-2xl font-bold ${stats.new_submissions > 0 ? "text-discovery-warn" : "text-discovery-text"}`}
          data-testid="admin-stats-new-submissions"
        >
          {stats.new_submissions}
        </p>
        {stats.new_submissions > 0 ? (
          <p className="mt-1 text-[11px] text-discovery-warn">Perlu ditinjau</p>
        ) : (
          <p className="mt-1 text-[11px] text-discovery-muted">Semua sudah ditinjau</p>
        )}
      </Card>
      <Card className="border-discovery-border bg-white p-4">
        <div className="flex items-center gap-2 text-xs text-discovery-muted">
          <Inbox size={13} /> Total Session
        </div>
        <p className="mt-1 text-2xl font-bold text-discovery-text" data-testid="admin-stats-total">{stats.total_sessions}</p>
        <p className="mt-1 text-[11px] text-discovery-muted">{stats.draft_sessions} draft, {stats.submitted_sessions} submitted</p>
      </Card>
      <Card className="border-discovery-border bg-white p-4">
        <div className="flex items-center gap-2 text-xs text-discovery-muted">
          <ClipboardCheck size={13} /> Submitted
        </div>
        <p className="mt-1 text-2xl font-bold text-discovery-success" data-testid="admin-stats-submitted">{stats.submitted_sessions}</p>
        <p className="mt-1 text-[11px] text-discovery-muted">Siap di-review</p>
      </Card>
      <Card className="border-discovery-border bg-white p-4">
        <div className="flex items-center gap-2 text-xs text-discovery-muted">
          <FileText size={13} /> Submisi Terakhir
        </div>
        {stats.latest_submission ? (
          <>
            <p className="mt-1 truncate text-sm font-semibold text-discovery-text" data-testid="admin-stats-latest-client">
              {stats.latest_submission.client_name}
            </p>
            <p className="mt-1 text-[11px] text-discovery-muted">
              {formatRelative(stats.latest_submission.submitted_at)}
            </p>
          </>
        ) : (
          <p className="mt-2 text-sm italic text-discovery-muted">Belum ada</p>
        )}
      </Card>
    </div>
  );
};
