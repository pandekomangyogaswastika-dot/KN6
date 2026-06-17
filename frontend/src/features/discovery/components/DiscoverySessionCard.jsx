/** DiscoverySessionCard — one row in the admin session list (info + actions). */
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader,
  AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Link2, Download, Trash2, Copy, ExternalLink,
  ClipboardCheck, Eye, BellRing, CheckCheck,
} from "lucide-react";
import { discoveryApi } from "../api";
import { formatDate, formatRelative } from "./discoveryFormat";

export const DiscoverySessionCard = ({ s, onNavigate, onCopy, onAcknowledge, onDelete, buildLink }) => (
  <Card
    data-testid={`admin-session-${s.id}`}
    className="border-discovery-border bg-white p-5 transition-shadow hover:shadow-discovery"
  >
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div className="flex-1">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <h3 className="text-lg font-semibold text-discovery-text">{s.client_name}</h3>
          {s.status === "submitted" ? (
            <Badge className="border-0 bg-discovery-success/15 text-[10px] font-semibold text-discovery-success">
              <ClipboardCheck size={10} className="mr-1" /> Submitted
            </Badge>
          ) : (
            <Badge variant="outline" className="border-discovery-border text-[10px] font-medium text-discovery-muted">
              Draft
            </Badge>
          )}
          {s.is_new_submission ? (
            <Badge
              data-testid={`admin-session-${s.id}-new-badge`}
              className="animate-pulse border-0 bg-discovery-warn text-[10px] font-bold uppercase tracking-widest text-white"
            >
              <BellRing size={10} className="mr-1" /> Baru!
            </Badge>
          ) : null}
        </div>
        {s.project_name ? (
          <p className="text-sm text-discovery-muted">Project: {s.project_name}</p>
        ) : null}
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-discovery-muted">
          {s.contact_person ? <span>👤 {s.contact_person}</span> : null}
          {s.contact_email ? <span>📧 {s.contact_email}</span> : null}
          <span>📅 {formatDate(s.created_at)}</span>
          {s.submitted_at ? (
            <span data-testid={`admin-session-${s.id}-submitted-at`}>
              ✅ Submitted {formatRelative(s.submitted_at)}
            </span>
          ) : null}
          <span className="font-semibold text-discovery-primary">
            {s.progress?.answered ?? 0}/{s.progress?.total ?? 0} terjawab ({s.progress?.percent ?? 0}%)
          </span>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {s.is_new_submission ? (
          <Button
            data-testid={`admin-session-${s.id}-acknowledge`}
            size="sm"
            onClick={() => onAcknowledge(s.id)}
            className="bg-discovery-warn text-white hover:bg-discovery-warn/85"
          >
            <CheckCheck size={13} className="mr-1.5" /> Tandai Sudah Dibaca
          </Button>
        ) : null}
        <Button
          data-testid={`admin-session-${s.id}-copy`}
          size="sm"
          variant="outline"
          onClick={() => onCopy(s.id)}
          className="border-discovery-border text-discovery-text hover:border-discovery-primary"
        >
          <Copy size={13} className="mr-1.5" /> Salin Link
        </Button>
        <Button
          data-testid={`admin-session-${s.id}-open`}
          size="sm"
          variant="outline"
          onClick={() => onNavigate(`/discovery/${s.id}`)}
          className="border-discovery-border text-discovery-text hover:border-discovery-primary"
        >
          <Eye size={13} className="mr-1.5" /> Buka
        </Button>
        <Button
          data-testid={`admin-session-${s.id}-pdf`}
          size="sm"
          variant="outline"
          onClick={() => window.open(discoveryApi.exportPdfUrl(s.id), "_blank")}
          className="border-discovery-accent/50 text-discovery-accent hover:bg-discovery-accent/10"
        >
          <Download size={13} className="mr-1.5" /> PDF
        </Button>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              data-testid={`admin-session-${s.id}-delete`}
              size="sm"
              variant="outline"
              className="border-discovery-danger/40 text-discovery-danger hover:bg-discovery-danger/10"
            >
              <Trash2 size={13} />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="border-discovery-border bg-white">
            <AlertDialogHeader>
              <AlertDialogTitle>Hapus session ini?</AlertDialogTitle>
              <AlertDialogDescription>
                Session <strong>{s.client_name}</strong> dan semua jawaban akan dihapus permanen.
                Tindakan ini tidak bisa di-undo.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Batal</AlertDialogCancel>
              <AlertDialogAction
                data-testid={`admin-session-${s.id}-delete-confirm`}
                onClick={() => onDelete(s.id)}
                className="bg-discovery-danger text-white hover:bg-discovery-danger/90"
              >
                Ya, Hapus
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
    <div className="mt-3 flex items-center gap-2 rounded-lg bg-discovery-bg-deep/40 px-3 py-2">
      <Link2 size={12} className="shrink-0 text-discovery-muted" />
      <code className="flex-1 truncate text-[11px] text-discovery-text">{buildLink(s.id)}</code>
      <a
        href={buildLink(s.id)}
        target="_blank"
        rel="noopener noreferrer"
        data-testid={`admin-session-${s.id}-open-link`}
        className="text-discovery-primary hover:text-discovery-primary-hover"
      >
        <ExternalLink size={12} />
      </a>
    </div>
  </Card>
);
