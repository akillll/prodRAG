"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { FileUp, LoaderCircle, RefreshCw, ShieldCheck } from "lucide-react";

type DocumentItem = {
  id: string;
  filename: string;
  status: "PROCESSING" | "READY" | "FAILED" | "DELETING";
  failure_reason: string | null;
  file_size_bytes: number;
  created_at: string;
};

type UploadResult = {
  id: string;
  filename: string;
  status: DocumentItem["status"];
  version_number: number;
  duplicate: boolean;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const statusClassNames: Record<DocumentItem["status"], string> = {
  PROCESSING: "bg-amber-100 text-amber-900 ring-amber-200",
  READY: "bg-emerald-100 text-emerald-900 ring-emerald-200",
  FAILED: "bg-rose-100 text-rose-900 ring-rose-200",
  DELETING: "bg-slate-200 text-slate-700 ring-slate-300",
};

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default function HomePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadDocuments() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/documents`);
      if (!response.ok) throw new Error("Unable to load documents.");
      setDocuments(await response.json());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load documents.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    fetch(`${apiBaseUrl}/documents`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load documents.");
        return (await response.json()) as DocumentItem[];
      })
      .then((loadedDocuments) => {
        if (active) setDocuments(loadedDocuments);
      })
      .catch((loadError: unknown) => {
        if (active) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load documents.");
        }
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    setSelectedFile(event.target.files?.[0] ?? null);
    setError(null);
    setNotice(null);
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setError("Choose a PDF, Markdown, or text file first.");
      return;
    }

    setIsUploading(true);
    setError(null);
    setNotice(null);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${apiBaseUrl}/documents`, { method: "POST", body: formData });
      const result = (await response.json()) as UploadResult | { detail?: string };
      if (!response.ok) {
        throw new Error("detail" in result ? result.detail : "Unable to upload the document.");
      }

      const uploaded = result as UploadResult;
      setNotice(
        uploaded.duplicate
          ? `${uploaded.filename} already exists and was not uploaded again.`
          : `${uploaded.filename} is stored and awaiting processing.`,
      );
      setSelectedFile(null);
      await loadDocuments();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Unable to upload the document.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f4f0e8] px-5 py-8 text-[#1d2a2e] sm:px-10 lg:px-16">
      <div className="mx-auto max-w-6xl">
        <header className="border-b border-[#c9c2b5] pb-7">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.22em] text-[#b45734]">
            <ShieldCheck className="size-4" /> prodRAG / Document desk
          </div>
          <div className="mt-5 flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <h1 className="font-[family-name:var(--font-editorial)] text-5xl leading-none tracking-tight sm:text-6xl">
                Build the evidence base.
              </h1>
              <p className="mt-4 max-w-xl text-base leading-7 text-[#536166]">
                Originals are retained with traceable processing state before they enter the RAG pipeline.
              </p>
            </div>
            <button
              className="inline-flex items-center gap-2 self-start border border-[#718084] bg-[#e7e1d6] px-4 py-2 text-sm font-semibold transition hover:bg-[#d8d0c2] md:self-auto"
              onClick={() => void loadDocuments()}
              type="button"
            >
              <RefreshCw className={`size-4 ${isLoading ? "animate-spin" : ""}`} /> Refresh
            </button>
          </div>
        </header>

        <section className="mt-8 grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
          <form className="border border-[#c9c2b5] bg-[#fffdf8] p-6 shadow-[6px_6px_0_#d6ccbc]" onSubmit={uploadDocument}>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#b45734]">Add source</p>
            <h2 className="mt-2 font-[family-name:var(--font-editorial)] text-3xl">Upload one document</h2>
            <p className="mt-3 text-sm leading-6 text-[#536166]">PDF, Markdown, and plain text are supported in this sprint.</p>
            <label className="mt-7 flex cursor-pointer flex-col items-center justify-center border border-dashed border-[#718084] bg-[#f4f0e8] px-5 py-9 text-center transition hover:bg-[#ece5d9]">
              <FileUp className="size-7 text-[#b45734]" />
              <span className="mt-3 text-sm font-semibold">{selectedFile?.name ?? "Choose a document"}</span>
              <span className="mt-1 text-xs text-[#667277]">{selectedFile ? formatBytes(selectedFile.size) : "One file at a time"}</span>
              <input accept=".pdf,.md,.txt" className="sr-only" onChange={selectFile} type="file" />
            </label>
            <button
              className="mt-5 inline-flex w-full items-center justify-center gap-2 bg-[#1d4a52] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#133940] disabled:cursor-not-allowed disabled:bg-[#829094]"
              disabled={isUploading}
              type="submit"
            >
              {isUploading ? <LoaderCircle className="size-4 animate-spin" /> : <FileUp className="size-4" />}
              {isUploading ? "Storing document..." : "Store document"}
            </button>
            {notice && <p className="mt-4 border-l-4 border-emerald-600 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{notice}</p>}
            {error && <p className="mt-4 border-l-4 border-rose-600 bg-rose-50 px-3 py-2 text-sm text-rose-900">{error}</p>}
          </form>

          <section aria-live="polite">
            <div className="flex items-baseline justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#b45734]">Corpus</p>
                <h2 className="mt-2 font-[family-name:var(--font-editorial)] text-3xl">Document register</h2>
              </div>
              <span className="text-sm text-[#536166]">{documents.length} total</span>
            </div>
            <div className="mt-5 divide-y divide-[#d8d0c2] border-y border-[#c9c2b5] bg-[#fffdf8]">
              {isLoading ? (
                <div className="flex items-center gap-2 px-5 py-8 text-sm text-[#536166]"><LoaderCircle className="size-4 animate-spin" /> Loading register...</div>
              ) : documents.length === 0 ? (
                <p className="px-5 py-8 text-sm leading-6 text-[#536166]">No documents stored yet. Add the first source to begin the ingestion pipeline.</p>
              ) : (
                documents.map((document) => (
                  <article className="px-5 py-4" key={document.id}>
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <h3 className="font-semibold break-all">{document.filename}</h3>
                        <p className="mt-1 text-xs text-[#667277]">{formatBytes(document.file_size_bytes)} · Added {new Date(document.created_at).toLocaleString()}</p>
                      </div>
                      <span className={`rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${statusClassNames[document.status]}`}>{document.status}</span>
                    </div>
                    {document.failure_reason && <p className="mt-3 text-sm text-rose-800">{document.failure_reason}</p>}
                  </article>
                ))
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
