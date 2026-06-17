import { useState } from "react";
import { HelpButton } from "./HelpButton";
import { AttachmentUploader } from "./AttachmentUploader";
import { QuestionInput } from "./QuestionInput";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Check, SkipForward, Eraser, StickyNote, X } from "lucide-react";

const SkipPill = ({ active, onToggle, locked, testId }) => (
  <button
    type="button"
    data-testid={testId}
    disabled={locked}
    onClick={onToggle}
    className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
      active
        ? "border-discovery-warn bg-discovery-warn/10 text-discovery-warn"
        : "border-discovery-border bg-white text-discovery-muted hover:border-discovery-primary hover:text-discovery-primary"
    }`}
  >
    <SkipForward size={12} />
    {active ? "Dilewati" : "Lewati"}
  </button>
);

export const QuestionField = ({
  index,
  question,
  answer,
  onChange,
  onOtherChange,
  onNoteChange,
  onSkip,
  onClear,
  locked = false,
  sessionId,
  attachments = [],
  onAttachmentUploaded,
  onAttachmentDeleted,
}) => {
  const skipped = answer?.skipped === true;
  const hasValue = answer && !skipped && answer.value !== null && answer.value !== "" && !(Array.isArray(answer.value) && answer.value.length === 0);
  const [touched, setTouched] = useState(false);
  const [showNote, setShowNote] = useState(() => Boolean(answer?.note));
  const testIdBase = `question-${question.id}`;

  return (
    <div
      data-testid={`${testIdBase}-card`}
      className={`rounded-2xl border bg-white p-5 transition-all ${
        hasValue
          ? "border-discovery-accent/50 shadow-discovery"
          : skipped
          ? "border-discovery-warn/40"
          : "border-discovery-border hover:border-discovery-primary/40"
      }`}
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <Badge
              variant="outline"
              className="border-discovery-primary/20 bg-discovery-soft text-[10px] font-bold uppercase tracking-wider text-discovery-primary"
            >
              Q{String(index).padStart(2, "0")} · {question.id}
            </Badge>
            {hasValue ? (
              <Badge className="border-0 bg-discovery-accent/10 text-[10px] font-semibold text-discovery-accent">
                <Check size={11} className="mr-1" /> Terisi
              </Badge>
            ) : null}
          </div>
          <p className="text-[15px] font-semibold leading-snug text-discovery-text">
            {question.prompt}
          </p>
        </div>
        <HelpButton helpText={question.help} testId={`${testIdBase}-help`} />
      </div>

      <div className="mt-4">
        <QuestionInput
          question={question}
          answer={answer}
          skipped={skipped}
          locked={locked}
          onChange={onChange}
          onOtherChange={onOtherChange}
          onTouched={() => setTouched(true)}
          testIdBase={testIdBase}
        />
      </div>

      {!skipped ? (
        <div className="mt-3" data-testid={`${testIdBase}-note-section`}>
          {showNote || answer?.note ? (
            <div className="rounded-lg border border-discovery-border bg-discovery-bg/40 p-3">
              <div className="mb-1.5 flex items-center justify-between">
                <Label className="flex items-center gap-1.5 text-xs font-medium text-discovery-muted">
                  <StickyNote size={12} /> Catatan tambahan (opsional)
                </Label>
                {!answer?.note ? (
                  <button
                    type="button"
                    data-testid={`${testIdBase}-note-close`}
                    onClick={() => setShowNote(false)}
                    disabled={locked}
                    className="text-discovery-muted transition-colors hover:text-discovery-danger disabled:opacity-50"
                    aria-label="Tutup catatan"
                  >
                    <X size={13} />
                  </button>
                ) : null}
              </div>
              <Textarea
                data-testid={`${testIdBase}-note`}
                value={answer?.note ?? ""}
                onChange={(e) => onNoteChange?.(e.target.value)}
                disabled={locked}
                rows={2}
                placeholder="Tambahkan konteks, asumsi, atau penjelasan tambahan…"
                className="border-discovery-border bg-white text-sm focus:border-discovery-primary focus-visible:ring-discovery-primary/30"
              />
            </div>
          ) : (
            <button
              type="button"
              data-testid={`${testIdBase}-add-note`}
              onClick={() => setShowNote(true)}
              disabled={locked}
              className="inline-flex items-center gap-1.5 rounded-full border border-dashed border-discovery-border bg-white px-3 py-1 text-xs font-medium text-discovery-muted transition-all hover:border-discovery-primary hover:text-discovery-primary disabled:opacity-50"
            >
              <StickyNote size={12} /> Tambah catatan
            </button>
          )}
        </div>
      ) : null}

      {sessionId ? (
        <AttachmentUploader
          sessionId={sessionId}
          questionId={question.id}
          attachments={attachments}
          locked={locked}
          onUploaded={onAttachmentUploaded}
          onDeleted={onAttachmentDeleted}
        />
      ) : null}

      <div className="mt-4 flex items-center justify-between gap-3 border-t border-discovery-border pt-3">
        <p className="text-[11px] text-discovery-muted">
          {touched ? <em>Tersimpan otomatis</em> : <span>Boleh diisi nanti atau dilewati</span>}
        </p>
        <div className="flex items-center gap-2">
          {hasValue && !skipped ? (
            <button
              type="button"
              data-testid={`${testIdBase}-clear`}
              disabled={locked}
              onClick={onClear}
              className="inline-flex items-center gap-1.5 rounded-full border border-discovery-border bg-white px-3 py-1 text-xs font-medium text-discovery-muted transition-all hover:border-discovery-danger hover:text-discovery-danger disabled:opacity-50"
            >
              <Eraser size={12} /> Hapus
            </button>
          ) : null}
          <SkipPill active={skipped} onToggle={onSkip} locked={locked} testId={`${testIdBase}-skip`} />
        </div>
      </div>
    </div>
  );
};
