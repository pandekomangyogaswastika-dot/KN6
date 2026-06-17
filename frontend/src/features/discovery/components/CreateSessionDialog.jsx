/** CreateSessionDialog — modal form to create a new discovery session. */
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Plus, Loader2 } from "lucide-react";

export const CreateSessionDialog = ({ open, onOpenChange, form, setForm, creating, onSubmit }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogTrigger asChild>
      <Button
        data-testid="admin-create-session"
        className="bg-discovery-primary text-white hover:bg-discovery-primary-hover"
      >
        <Plus size={14} className="mr-1.5" /> Buat Session Baru
      </Button>
    </DialogTrigger>
    <DialogContent className="border-discovery-border bg-white">
      <DialogHeader>
        <DialogTitle className="text-discovery-text">Buat Session Discovery</DialogTitle>
        <DialogDescription className="text-discovery-muted">
          Isi data klien. Setelah create, link akan otomatis disalin ke clipboard.
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-3 py-2">
        <div>
          <Label htmlFor="client_name" className="text-discovery-text">Nama Klien <span className="text-discovery-danger">*</span></Label>
          <Input
            id="client_name"
            data-testid="admin-form-client-name"
            value={form.client_name}
            onChange={(e) => setForm({ ...form, client_name: e.target.value })}
            placeholder="PT. Kain Nusantara"
            className="border-discovery-border focus:border-discovery-primary"
          />
        </div>
        <div>
          <Label htmlFor="project_name" className="text-discovery-text">Nama Project</Label>
          <Input
            id="project_name"
            data-testid="admin-form-project-name"
            value={form.project_name}
            onChange={(e) => setForm({ ...form, project_name: e.target.value })}
            placeholder="ERP Implementation 2026"
            className="border-discovery-border focus:border-discovery-primary"
          />
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <Label htmlFor="contact_person" className="text-discovery-text">Contact Person</Label>
            <Input
              id="contact_person"
              data-testid="admin-form-contact-person"
              value={form.contact_person}
              onChange={(e) => setForm({ ...form, contact_person: e.target.value })}
              placeholder="Budi Santoso"
              className="border-discovery-border focus:border-discovery-primary"
            />
          </div>
          <div>
            <Label htmlFor="contact_email" className="text-discovery-text">Email</Label>
            <Input
              id="contact_email"
              type="email"
              data-testid="admin-form-contact-email"
              value={form.contact_email}
              onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
              placeholder="budi@klien.com"
              className="border-discovery-border focus:border-discovery-primary"
            />
          </div>
        </div>
        <div>
          <Label htmlFor="notes" className="text-discovery-text">Catatan Internal (opsional)</Label>
          <Textarea
            id="notes"
            data-testid="admin-form-notes"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Catatan untuk tim vendor — tidak ditampilkan ke klien"
            rows={2}
            className="border-discovery-border focus:border-discovery-primary"
          />
        </div>
      </div>
      <DialogFooter>
        <Button
          variant="outline"
          data-testid="admin-form-cancel"
          onClick={() => onOpenChange(false)}
          className="border-discovery-border"
        >
          Batal
        </Button>
        <Button
          data-testid="admin-form-submit"
          onClick={onSubmit}
          disabled={creating || !form.client_name.trim()}
          className="bg-discovery-primary text-white hover:bg-discovery-primary-hover"
        >
          {creating ? <Loader2 size={14} className="mr-1.5 animate-spin" /> : <Plus size={14} className="mr-1.5" />}
          {creating ? "Membuat..." : "Buat & Salin Link"}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);
