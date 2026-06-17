import { useEffect, useState } from "react";
import { discoveryApi } from "./api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, FileText, RefreshCw, ShieldCheck, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { CreateSessionDialog } from "./components/CreateSessionDialog";
import { DiscoveryStatsBanner } from "./components/DiscoveryStatsBanner";
import { DiscoverySessionCard } from "./components/DiscoverySessionCard";

/**
 * DiscoveryAdmin — vendor console untuk mengelola session discovery.
 * Sub-components (dialog, stats banner, session card, date utils) berada di
 * ./components/ agar file ini tetap di bawah batas ukuran (KN_02).
 */
export const DiscoveryAdmin = ({ onNavigate }) => {
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ client_name: "", project_name: "", contact_person: "", contact_email: "", notes: "" });

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [sList, sStats] = await Promise.all([
        discoveryApi.listSessions(),
        discoveryApi.fetchStats(),
      ]);
      setSessions(sList);
      setStats(sStats);
    } catch {
      toast({ title: "Gagal memuat", description: "Tidak bisa ambil daftar session.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // Auto-refresh setiap 30 detik agar badge "New" responsif
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, []);

  const buildLink = (sessionId) => `${window.location.origin}/discovery/${sessionId}`;

  const copyLink = async (sessionId) => {
    try {
      await navigator.clipboard.writeText(buildLink(sessionId));
      toast({ title: "Tersalin", description: "Link discovery sudah disalin ke clipboard." });
    } catch {
      toast({ title: "Tidak bisa salin", description: "Salin manual dari kolom Link.", variant: "destructive" });
    }
  };

  const submitCreate = async () => {
    if (!form.client_name.trim()) {
      toast({ title: "Wajib diisi", description: "Client Name tidak boleh kosong.", variant: "destructive" });
      return;
    }
    setCreating(true);
    try {
      const created = await discoveryApi.createSession({
        client_name: form.client_name.trim(),
        project_name: form.project_name.trim() || null,
        contact_person: form.contact_person.trim() || null,
        contact_email: form.contact_email.trim() || null,
        notes: form.notes.trim() || null,
      });
      setShowCreate(false);
      setForm({ client_name: "", project_name: "", contact_person: "", contact_email: "", notes: "" });
      await fetchAll();
      // Auto-copy link
      try {
        await navigator.clipboard.writeText(buildLink(created.id));
        toast({ title: "Session dibuat", description: "Link sudah disalin ke clipboard." });
      } catch {
        toast({ title: "Session dibuat", description: `ID: ${created.id}` });
      }
    } catch (e) {
      const detail = e?.response?.data?.detail || "Gagal create session.";
      toast({ title: "Error", description: detail, variant: "destructive" });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (sessionId) => {
    try {
      await discoveryApi.deleteSession(sessionId);
      await fetchAll();
      toast({ title: "Session dihapus" });
    } catch {
      toast({ title: "Gagal menghapus", variant: "destructive" });
    }
  };

  const handleAcknowledge = async (sessionId) => {
    try {
      await discoveryApi.acknowledgeSession(sessionId);
      await fetchAll();
      toast({ title: "Submission ditandai sudah dibaca" });
    } catch {
      toast({ title: "Gagal acknowledge", variant: "destructive" });
    }
  };

  return (
    <div className="min-h-screen px-4 py-8 sm:px-6">
      <div className="mx-auto w-full max-w-6xl">
        <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-discovery-primary text-xs font-bold text-white">KN</span>
              <Badge className="border-0 bg-discovery-soft text-[10px] font-semibold uppercase tracking-widest text-discovery-primary">
                <ShieldCheck size={10} className="mr-1" /> Vendor Console
              </Badge>
            </div>
            <h1 className="text-2xl font-bold text-discovery-text sm:text-3xl">Discovery E-Questionnaire</h1>
            <p className="mt-1 max-w-2xl text-sm leading-relaxed text-discovery-muted">
              Buat dan kelola session discovery untuk setiap klien. Setiap session menghasilkan link unik
              yang bisa Anda kirim ke klien — tanpa perlu login.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              data-testid="admin-refresh"
              variant="outline"
              onClick={fetchAll}
              className="border-discovery-border text-discovery-text hover:border-discovery-primary"
            >
              <RefreshCw size={14} className={`mr-1.5 ${loading ? "animate-spin" : ""}`} /> Refresh
            </Button>
            <CreateSessionDialog
              open={showCreate}
              onOpenChange={setShowCreate}
              form={form}
              setForm={setForm}
              creating={creating}
              onSubmit={submitCreate}
            />
          </div>
        </header>

        {loading ? (
          <Card className="border-discovery-border p-8 text-center">
            <Loader2 size={20} className="mx-auto animate-spin text-discovery-muted" />
            <p className="mt-2 text-sm text-discovery-muted">Memuat session...</p>
          </Card>
        ) : (
          <>
            <DiscoveryStatsBanner stats={stats} />

            {sessions.length === 0 ? (
              <Card className="border-2 border-dashed border-discovery-border bg-white p-12 text-center">
                <FileText size={40} className="mx-auto mb-3 text-discovery-muted" />
                <h3 className="mb-1 text-lg font-semibold text-discovery-text">Belum ada session</h3>
                <p className="mb-4 text-sm text-discovery-muted">
                  Klik tombol "Buat Session Baru" untuk membuat link discovery pertama Anda.
                </p>
                <Button
                  data-testid="admin-empty-create"
                  onClick={() => setShowCreate(true)}
                  className="bg-discovery-primary text-white hover:bg-discovery-primary-hover"
                >
                  <Plus size={14} className="mr-1.5" /> Buat Session Baru
                </Button>
              </Card>
            ) : (
              <div className="grid gap-3">
                {sessions.map((s) => (
                  <DiscoverySessionCard
                    key={s.id}
                    s={s}
                    onNavigate={onNavigate}
                    onCopy={copyLink}
                    onAcknowledge={handleAcknowledge}
                    onDelete={handleDelete}
                    buildLink={buildLink}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
