"use client";
import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Plus, X } from "lucide-react";

export type NewDrugPayload = {
  title: string;
  genericName: string;
  therapeuticArea: string;
  din: string;
  organization: string;
  submissionDate?: string;
  projectNumber?: string;
  description?: string;
  documents?: File[];
};

export default function AddDrugModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: NewDrugPayload) => void;
}) {
  const [mounted, setMounted] = useState(false);

  // ---------- form state (declare BEFORE usage) ----------
  const [title, setTitle] = useState("");
  const [genericName, setGenericName] = useState("");
  const [therapeuticArea, setTherapeuticArea] = useState("");
  const [din, setDIN] = useState("");
  const [organization, setOrganization] = useState("");
  const [submissionDate, setSubmissionDate] = useState<string>("");
  const [projectNumber, setProjectNumber] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [documents, setDocuments] = useState<File[] | undefined>(undefined);
  const [errors, setErrors] = useState<string[]>([]);

  // ---------- effects ----------
  useEffect(() => setMounted(true), []);

  // lock scroll + Esc to close when open
  useEffect(() => {
    if (!open) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  // ---------- helpers ----------
  function validate() {
    const e: string[] = [];
    if (!title.trim()) e.push("Title is required.");
    if (!genericName.trim()) e.push("Generic name is required.");
    if (!therapeuticArea.trim()) e.push("Therapeutic area is required.");
    if (!din.trim()) e.push("DIN is required.");
    if (!organization.trim()) e.push("Organization is required.");
    return e;
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (errs.length) return setErrors(errs);
    onSubmit({
      title: title.trim(),
      genericName: genericName.trim(),
      therapeuticArea: therapeuticArea.trim(),
      din: din.trim(),
      organization: organization.trim(),
      submissionDate: submissionDate || undefined,
      projectNumber: projectNumber || undefined,
      description: description || undefined,
      documents,
    });
    onClose();
  }

  // small field helper (declared before use)
  function Field({
    label,
    value,
    onChange,
    inputType,
  }: {
    label: string;
    value: string;
    onChange: (v: string) => void;
    inputType: "text" | "date";
  }) {
    return (
      <div>
        <label className="block text-sm font-medium">{label}</label>
        <input
          type={inputType}
          className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    );
  }

  if (!open || !mounted) return null;

  // ---------- modal JSX ----------
  const modal = (
    <div
      className="fixed inset-0 z-[100]"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-drug-title"
    >
      {/* Backdrop with blur (full viewport) */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div
        className="relative z-[110] mx-auto mt-20 w-full max-w-2xl rounded-2xl
                   bg-[var(--bars)] text-[var(--foreground)] p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 id="add-drug-title" className="text-xl font-semibold">
            Add New Drug (My Drugs)
          </h3>
          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-[var(--hover-bg)]"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {errors.length > 0 && (
          <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            <ul className="list-disc pl-5">
              {errors.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          </div>
        )}

        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field label="Title *" value={title} onChange={setTitle} inputType="text" />
            <Field
              label="Generic name *"
              value={genericName}
              onChange={setGenericName}
              inputType="text"
            />
            <Field
              label="Therapeutic area *"
              value={therapeuticArea}
              onChange={setTherapeuticArea}
              inputType="text"
            />
            <Field label="DIN *" value={din} onChange={setDIN} inputType="text" />
            <Field
              label="Organization *"
              value={organization}
              onChange={setOrganization}
              inputType="text"
            />
            <Field
              label="Submission date"
              value={submissionDate}
              onChange={setSubmissionDate}
              inputType="date"
            />
            <Field
              label="Project number"
              value={projectNumber}
              onChange={setProjectNumber}
              inputType="text"
            />

            <div className="md:col-span-2">
              <label className="mb-1 block text-sm font-medium">Additional description</label>
              <textarea
                className="h-24 w-full rounded-xl border px-3 py-2 outline-none
                           bg-[var(--input-bg)] text-[var(--input-text)]
                           focus:ring-2 focus:ring-rose-400"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="md:col-span-2">
              <label className="mb-1 block text-sm font-medium">Upload documents (optional)</label>
              <input
                type="file"
                multiple
                className="w-full rounded-xl border px-3 py-2
                           bg-[var(--input-bg)] text-[var(--input-text)]"
                onChange={(e) =>
                  setDocuments(e.target.files ? Array.from(e.target.files) : undefined)
                }
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border px-4 py-2 hover:bg-[var(--hover-bg)]"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-xl
                         bg-gradient-to-r from-rose-500 to-red-500
                         px-4 py-2 font-medium text-white shadow hover:opacity-90"
            >
              <Plus className="h-4 w-4" /> Add Drug
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  // render at <body> so nothing clips it
  return createPortal(modal, document.body);
}
