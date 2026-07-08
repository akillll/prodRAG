export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6">
      <p className="text-sm uppercase tracking-wide text-slate-500">prodRAG</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
        Evaluation-driven RAG system
      </h1>
      <p className="mt-4 text-lg leading-8 text-slate-700">
        The frontend shell is ready. Document upload, chat, citations, retrieval debugging,
        and evaluation screens will be added as their sprints begin.
      </p>
    </main>
  );
}
