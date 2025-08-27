"use client";
import React, { useState } from "react";
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
  if (!open) return null;

  // --- form state ---
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

  return (
    <div className="fixed inset-0 z-[70]">
      {/* backdrop w/ blur */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 mx-auto mt-20 w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl dark:bg-neutral-900">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-xl font-semibold">Add New Drug (My Drugs)</h3>
          <button onClick={onClose} className="rounded-lg p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {errors.length > 0 && (
          <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            <ul className="list-disc pl-5">{errors.map((e) => <li key={e}>{e}</li>)}</ul>
          </div>
        )}

        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium">Title *</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={title} onChange={(e)=>setTitle(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Generic name *</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={genericName} onChange={(e)=>setGenericName(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Therapeutic area *</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={therapeuticArea} onChange={(e)=>setTherapeuticArea(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">DIN *</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={din} onChange={(e)=>setDIN(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Organization *</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={organization} onChange={(e)=>setOrganization(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Submission date</label>
              <input type="date" className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={submissionDate} onChange={(e)=>setSubmissionDate(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Project number</label>
              <input className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                     value={projectNumber} onChange={(e)=>setProjectNumber(e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <label className="mb-1 block text-sm font-medium">Additional description</label>
              <textarea className="h-24 w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-rose-400 dark:bg-neutral-800"
                        value={description} onChange={(e)=>setDescription(e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <label className="mb-1 block text-sm font-medium">Upload documents (optional)</label>
              <input type="file" multiple className="w-full rounded-xl border px-3 py-2 dark:bg-neutral-800"
                     onChange={(e)=> setDocuments(e.target.files ? Array.from(e.target.files) : undefined)} />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="rounded-xl border px-4 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-800">
              Cancel
            </button>
            <button type="submit" className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-rose-500 to-red-500 px-4 py-2 font-medium text-white shadow hover:opacity-90">
              <Plus className="h-4 w-4" /> Add Drug
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
