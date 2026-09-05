const TONE: Record<string, string> = {
  open: "bg-ink/10 text-ink border-ink/20",
  submitted: "bg-ink/10 text-ink border-ink/20",
  requested: "bg-ink/10 text-ink border-ink/20",
  pending: "bg-ochre/15 text-ochre border-ochre/30",
  scheduled: "bg-ochre/15 text-ochre border-ochre/30",
  assigned: "bg-ochre/15 text-ochre border-ochre/30",
  in_progress: "bg-ochre/15 text-ochre border-ochre/30",
  in_transit: "bg-ochre/15 text-ochre border-ochre/30",
  countered: "bg-ochre/15 text-ochre border-ochre/30",
  accepted: "bg-success/15 text-success border-success/30",
  approved: "bg-success/15 text-success border-success/30",
  delivered: "bg-success/15 text-success border-success/30",
  completed: "bg-success/15 text-success border-success/30",
  issued: "bg-success/15 text-success border-success/30",
  rejected: "bg-danger/15 text-danger border-danger/30",
  disputed: "bg-danger/15 text-danger border-danger/30",
  cancelled: "bg-olive/15 text-olive border-olive/30",
  closed: "bg-olive/15 text-olive border-olive/30",
};

export function StatusBadge({ status }: { status: string }) {
  const cls = TONE[status] ?? "bg-olive/15 text-olive border-olive/30";
  return (
    <span className={`inline-block rounded-sm border px-2 py-0.5 text-xs font-medium ${cls}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}
