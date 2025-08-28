"use client";
import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Plus, X } from "lucide-react";
import { NewDrugPayload } from "@/lib/api";

enum DrugType {
  BIOLOGIC = "biologic",
  RARE_DISEASE = "rare_disease",
  ONCOLOGY = "oncology",
  STANDARD = "standard",
}

enum SubmissionPathway {
  STANDARD = "standard",
  PRIORITY = "priority",
  CONDITIONAL = "conditional",
}

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
  const [costEffectiveness, setCostEffectiveness] = useState<string>("");
  const [therapeuticValue, setTherapeuticValue] = useState<string>("");
  const [manufacturerPrice, setManufacturerPrice] = useState<string>("");
  const [reimbursementRestrictions, setReimbursementRestrictions] = useState<string>("");
  const [drugType, setDrugType] = useState<DrugType>(DrugType.BIOLOGIC);
  const [submissionPathway, setSubmissionPathway] = useState<SubmissionPathway>(
    SubmissionPathway.STANDARD
  );
  const [dosageForm, setDosageForm] = useState<string>("");
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

    if (!therapeuticValue.trim()) e.push("Therapeutic value is required.");
    if (!submissionPathway.trim()) e.push("Submission pathway is required.");
    if (!drugType.trim()) e.push("Drug type is required.");
    if (!dosageForm.trim()) e.push("Dosage form is required");

    const costEffNum = Number(costEffectiveness.trim());
    if (!costEffectiveness.trim()) {
      e.push("Cost effectiveness is required.");
    } else if (isNaN(costEffNum)) {
      e.push("Cost effectiveness must be a number.");
    } else if (costEffNum < 0) {
      e.push("Cost effectiveness must be a positive number.");
    }

    const manufacturerPriceNum = Number(manufacturerPrice.trim());
    if (!manufacturerPrice.trim()) {
      e.push("Manufacturer price is required.");
    } else if (isNaN(manufacturerPriceNum)) {
      e.push("Manufacturer price must be a number.");
    } else if (manufacturerPriceNum < 0) {
      e.push("Manufacturer price must be a positive number.");
    }

    if (!reimbursementRestrictions.trim()) e.push("Reimbursement restrictions are required.");

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

      therapeuticValue: therapeuticValue.trim(),
      submissionPathway: submissionPathway.trim(),
      drugType: drugType.trim(),
      dosageForm: dosageForm.trim(),
      costEffectiveness: Number(costEffectiveness),
      manufacturerPrice: Number(manufacturerPrice),
      reimbursementRestrictions: reimbursementRestrictions.trim(),
    });

    onClose();
  }

  // small field helper (declared before use)
  // FIELDS WERE LOSING FOCUS WHEN TESTED DUE TO REGEN AFTER EACH LETTER TYPED, 
  // OPTED TO USE MANUALLY IN MODAL
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

  if (!mounted) return null;

  // ---------- modal JSX ----------
  const modal = (
    <div
      className={`fixed inset-0 z-[100] transition-opacity ${open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
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
            <div>
              <label className="block text-sm font-medium">Title *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Generic name *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={genericName}
                onChange={(e) => setGenericName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Therapeutic area *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={therapeuticArea}
                onChange={(e) => setTherapeuticArea(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Therapeutic value *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={therapeuticValue}
                onChange={(e) => setTherapeuticValue(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">DIN *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={din}
                onChange={(e) => setDIN(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Organization *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Cost effectiveness *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={costEffectiveness}
                onChange={(e) => setCostEffectiveness(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Manufacturer price *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={manufacturerPrice}
                onChange={(e) => setManufacturerPrice(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Reimbursement restrictions *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={reimbursementRestrictions}
                onChange={(e) => setReimbursementRestrictions(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Drug type *</label>
              <label>
                Drug Type:
                <select
                  value={drugType}
                  onChange={(e) => setDrugType(e.target.value as DrugType)}
                >
                  {Object.values(DrugType).map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium">Dosage form *</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={dosageForm}
                onChange={(e) => setDosageForm(e.target.value)}
              />
            </div>
            <label>
              Submission Pathway:
              <select
                value={submissionPathway}
                onChange={(e) =>
                  setSubmissionPathway(e.target.value as SubmissionPathway)
                }
              >
                {Object.values(SubmissionPathway).map((path) => (
                  <option key={path} value={path}>
                    {path}
                  </option>
                ))}
              </select>
            </label>
            <div>
              <label className="block text-sm font-medium">Submission date </label>
              <input
                type="date"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={submissionDate}
                onChange={(e) => setSubmissionDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Project number</label>
              <input
                type="text"
                className="w-full rounded-xl border px-3 outline-none
                     bg-[var(--input-bg)] text-[var(--input-text)]
                     focus:ring-2 focus:ring-rose-400"
                value={projectNumber}
                onChange={(e) => setProjectNumber(e.target.value)}
              />
            </div>

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
