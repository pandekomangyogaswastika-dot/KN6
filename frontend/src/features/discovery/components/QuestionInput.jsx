/**
 * QuestionInput — renders the actual input control for a discovery question,
 * switching on question.type. Extracted from QuestionField.jsx to keep both
 * files under the size limit (KN_02).
 */
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";

export const OTHER_VALUE = "__other__";
export const toArray = (val) => (Array.isArray(val) ? val : []);

export const ScaleSelector = ({ value, onChange, labels = {}, disabled, testIdBase }) => {
  const numbers = [1, 2, 3, 4, 5];
  const currentLabel = value ? labels[String(value)] : null;
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {numbers.map((n) => {
          const active = String(value) === String(n);
          return (
            <button
              key={n}
              type="button"
              data-testid={`${testIdBase}-scale-${n}`}
              disabled={disabled}
              onClick={() => onChange(n)}
              className={`flex h-12 min-w-[3rem] flex-col items-center justify-center rounded-xl border px-3 text-sm font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
                active
                  ? "border-discovery-primary bg-discovery-primary text-white shadow-discovery"
                  : "border-discovery-border bg-white text-discovery-text hover:border-discovery-primary hover:bg-discovery-soft"
              }`}
            >
              <span>{n}</span>
              {labels[String(n)] ? (
                <span className={`mt-0.5 text-[10px] font-medium ${active ? "text-white/85" : "text-discovery-muted"}`}>
                  {n === 1 ? "min" : n === 5 ? "max" : ""}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
      {labels && (labels["1"] || labels["3"] || labels["5"]) ? (
        <div className="flex justify-between text-[11px] text-discovery-muted">
          <span>1 — {labels["1"] || ""}</span>
          <span className="text-center">{labels["3"] ? `3 — ${labels["3"]}` : ""}</span>
          <span>5 — {labels["5"] || ""}</span>
        </div>
      ) : null}
      {currentLabel ? (
        <p data-testid={`${testIdBase}-scale-feedback`} className="text-xs italic text-discovery-primary">
          Pilihan Anda: <span className="font-semibold">{value}/5 — {currentLabel}</span>
        </p>
      ) : null}
    </div>
  );
};

export const QuestionInput = ({ question, answer, skipped, locked, onChange, onOtherChange, onTouched, testIdBase }) => {
  const renderOtherInput = () => (
    <Input
      data-testid={`${testIdBase}-other-input`}
      value={answer?.other_text ?? ""}
      onChange={(e) => onOtherChange?.(e.target.value)}
      onBlur={onTouched}
      disabled={locked}
      placeholder="Tulis pilihan Anda sendiri…"
      className="border-discovery-warn/50 bg-discovery-warn/5 focus:border-discovery-primary focus-visible:ring-discovery-primary/30"
    />
  );

  if (skipped) {
    return (
      <div className="rounded-lg border border-dashed border-discovery-warn/60 bg-discovery-warn/5 px-4 py-3 text-sm italic text-discovery-warn">
        Pertanyaan ini ditandai “dilewati”. Klik tombol Lewati lagi untuk mengisi.
      </div>
    );
  }

  switch (question.type) {
    case "single_choice": {
      const isOther = answer?.value === OTHER_VALUE;
      return (
        <div className="space-y-3">
          <RadioGroup
            data-testid={`${testIdBase}-radio`}
            value={answer?.value ?? ""}
            onValueChange={(v) => onChange(v)}
            disabled={locked}
            className="grid gap-2"
          >
            {question.options?.map((opt) => (
              <Label
                key={opt.value}
                htmlFor={`${question.id}-${opt.value}`}
                data-testid={`${testIdBase}-opt-${opt.value}`}
                className={`flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 text-sm transition-all hover:border-discovery-primary hover:bg-discovery-soft ${
                  answer?.value === opt.value
                    ? "border-discovery-primary bg-discovery-soft text-discovery-primary shadow-discovery"
                    : "border-discovery-border bg-white text-discovery-text"
                }`}
              >
                <RadioGroupItem value={opt.value} id={`${question.id}-${opt.value}`} className="shrink-0" />
                <span className="flex-1 leading-snug">{opt.label}</span>
              </Label>
            ))}
            <Label
              htmlFor={`${question.id}-${OTHER_VALUE}`}
              data-testid={`${testIdBase}-opt-other`}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border border-dashed px-4 py-3 text-sm transition-all hover:border-discovery-primary hover:bg-discovery-soft ${
                isOther
                  ? "border-discovery-primary bg-discovery-soft text-discovery-primary shadow-discovery"
                  : "border-discovery-border bg-white text-discovery-text"
              }`}
            >
              <RadioGroupItem value={OTHER_VALUE} id={`${question.id}-${OTHER_VALUE}`} className="shrink-0" />
              <span className="flex-1 leading-snug">Lainnya…</span>
            </Label>
          </RadioGroup>
          {isOther ? renderOtherInput() : null}
        </div>
      );
    }

    case "multi_choice": {
      const arrVal = toArray(answer?.value);
      const max = question.max_select;
      const selectedReal = arrVal.filter((v) => v !== OTHER_VALUE);
      const otherChecked = arrVal.includes(OTHER_VALUE);
      return (
        <div className="space-y-2">
          {max ? (
            <p className="text-xs text-discovery-muted">
              Maks {max} pilihan. Terpilih: <span className="font-semibold text-discovery-primary">{selectedReal.length}/{max}</span>
            </p>
          ) : null}
          <div className="grid gap-2 sm:grid-cols-2">
            {question.options?.map((opt) => {
              const checked = arrVal.includes(opt.value);
              const reachedMax = max && selectedReal.length >= max && !checked;
              return (
                <Label
                  key={opt.value}
                  htmlFor={`${question.id}-${opt.value}`}
                  data-testid={`${testIdBase}-opt-${opt.value}`}
                  className={`flex cursor-pointer items-start gap-3 rounded-lg border px-4 py-3 text-sm transition-all ${
                    reachedMax ? "cursor-not-allowed opacity-50" : "hover:border-discovery-primary hover:bg-discovery-soft"
                  } ${
                    checked
                      ? "border-discovery-primary bg-discovery-soft text-discovery-primary shadow-discovery"
                      : "border-discovery-border bg-white text-discovery-text"
                  }`}
                >
                  <Checkbox
                    id={`${question.id}-${opt.value}`}
                    checked={checked}
                    disabled={locked || reachedMax}
                    onCheckedChange={(c) => {
                      const next = c ? [...arrVal, opt.value] : arrVal.filter((v) => v !== opt.value);
                      onChange(next);
                    }}
                    className="mt-0.5 shrink-0"
                  />
                  <span className="flex-1 leading-snug">{opt.label}</span>
                </Label>
              );
            })}
            <Label
              htmlFor={`${question.id}-${OTHER_VALUE}`}
              data-testid={`${testIdBase}-opt-other`}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border border-dashed px-4 py-3 text-sm transition-all hover:border-discovery-primary hover:bg-discovery-soft ${
                otherChecked
                  ? "border-discovery-primary bg-discovery-soft text-discovery-primary shadow-discovery"
                  : "border-discovery-border bg-white text-discovery-text"
              }`}
            >
              <Checkbox
                id={`${question.id}-${OTHER_VALUE}`}
                checked={otherChecked}
                disabled={locked}
                onCheckedChange={(c) => {
                  const next = c ? [...arrVal, OTHER_VALUE] : arrVal.filter((v) => v !== OTHER_VALUE);
                  onChange(next);
                }}
                className="mt-0.5 shrink-0"
              />
              <span className="flex-1 leading-snug">Lainnya…</span>
            </Label>
          </div>
          {otherChecked ? renderOtherInput() : null}
        </div>
      );
    }

    case "yes_no":
      return (
        <RadioGroup
          data-testid={`${testIdBase}-yesno`}
          value={answer?.value === true ? "yes" : answer?.value === false ? "no" : ""}
          onValueChange={(v) => onChange(v === "yes")}
          disabled={locked}
          className="flex flex-wrap gap-2"
        >
          {[
            { v: "yes", label: "Ya" },
            { v: "no", label: "Tidak" },
          ].map((opt) => {
            const active = (opt.v === "yes" && answer?.value === true) || (opt.v === "no" && answer?.value === false);
            return (
              <Label
                key={opt.v}
                htmlFor={`${question.id}-${opt.v}`}
                data-testid={`${testIdBase}-yesno-${opt.v}`}
                className={`flex min-w-[120px] cursor-pointer items-center justify-center gap-2 rounded-lg border px-5 py-3 text-sm font-medium transition-all hover:border-discovery-primary hover:bg-discovery-soft ${
                  active
                    ? "border-discovery-primary bg-discovery-primary text-white shadow-discovery"
                    : "border-discovery-border bg-white text-discovery-text"
                }`}
              >
                <RadioGroupItem value={opt.v} id={`${question.id}-${opt.v}`} className="sr-only" />
                {opt.label}
              </Label>
            );
          })}
        </RadioGroup>
      );

    case "scale_1_5":
      return (
        <ScaleSelector
          value={answer?.value}
          onChange={onChange}
          labels={question.scale_labels || {}}
          disabled={locked}
          testIdBase={testIdBase}
        />
      );

    case "text_short":
      return (
        <Input
          data-testid={`${testIdBase}-input`}
          value={answer?.value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          onBlur={onTouched}
          disabled={locked}
          placeholder="Tulis jawaban Anda..."
          className="border-discovery-border focus:border-discovery-primary focus-visible:ring-discovery-primary/30"
        />
      );

    case "text_long":
      return (
        <Textarea
          data-testid={`${testIdBase}-textarea`}
          value={answer?.value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          onBlur={onTouched}
          disabled={locked}
          placeholder="Tulis jawaban Anda di sini... (opsional)"
          rows={4}
          className="border-discovery-border focus:border-discovery-primary focus-visible:ring-discovery-primary/30"
        />
      );

    case "number":
      return (
        <Input
          type="number"
          data-testid={`${testIdBase}-number`}
          value={answer?.value ?? ""}
          onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))}
          onBlur={onTouched}
          disabled={locked}
          placeholder="Isi angka..."
          className="border-discovery-border focus:border-discovery-primary focus-visible:ring-discovery-primary/30"
        />
      );

    default:
      return <p className="text-sm italic text-discovery-muted">Tipe pertanyaan tidak dikenal: {question.type}</p>;
  }
};
