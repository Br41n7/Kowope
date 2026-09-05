"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/Button";
import { Select } from "@/components/Field";
import { listDocuments, uploadDocument } from "@/lib/endpoints";
import type { Document } from "@/lib/types";

const DOC_TYPES: { value: Document["doc_type"]; label: string }[] = [
  { value: "invoice", label: "Invoice" },
  { value: "certificate", label: "Certificate" },
  { value: "delivery_note", label: "Delivery note" },
  { value: "po", label: "Purchase order" },
  { value: "other", label: "Other" },
];

export function DocumentsPanel({ contentType, objectId }: { contentType: string; objectId: number }) {
  const [docs, setDocs] = useState<Document[]>([]);
  const [docType, setDocType] = useState<Document["doc_type"]>("invoice");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    listDocuments(contentType, objectId).then((data) => setDocs(Array.isArray(data) ? data : data.results));

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contentType, objectId]);

  const onUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      await uploadDocument({ content_type: contentType, object_id: objectId, doc_type: docType, file });
      setFile(null);
      load();
    } catch {
      setError("Upload failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="border border-line bg-white p-4">
      <h3 className="font-mono text-sm uppercase tracking-wide text-olive">Documents</h3>
      {docs.length === 0 && <p className="mt-2 text-xs text-olive">No documents uploaded yet.</p>}
      <ul className="mt-2 divide-y divide-line">
        {docs.map((d) => (
          <li key={d.id} className="flex items-center justify-between py-2 text-sm">
            <a href={d.file} target="_blank" rel="noreferrer" className="text-ochre underline">
              {d.doc_type} v{d.version}
            </a>
            <span className="text-xs text-olive">{d.uploaded_at.slice(0, 10)}</span>
          </li>
        ))}
      </ul>
      <form onSubmit={onUpload} className="mt-3 flex flex-wrap items-end gap-2">
        <Select value={docType} onChange={(e) => setDocType(e.target.value as Document["doc_type"])} className="w-40">
          {DOC_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </Select>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-xs text-olive file:mr-2 file:border file:border-line file:bg-white file:px-2 file:py-1 file:text-xs"
        />
        <Button type="submit" variant="secondary" disabled={busy || !file}>
          {busy ? "Uploading…" : "Upload"}
        </Button>
        {error && <p className="basis-full text-sm text-danger">{error}</p>}
      </form>
    </div>
  );
}
