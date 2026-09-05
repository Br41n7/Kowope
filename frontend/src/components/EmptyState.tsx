export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="border border-dashed border-line px-6 py-10 text-center">
      <p className="text-ink font-medium">{title}</p>
      {hint && <p className="mt-1 text-sm text-olive">{hint}</p>}
    </div>
  );
}
