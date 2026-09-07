interface Props {
  status: string;
  className?: string;
}

const STYLES: Record<string, string> = {
  VERIFIED: "bg-verified/10 text-verified border-verified/30",
  DEMO: "bg-demo/10 text-demo border-demo/30",
  UNVERIFIED: "bg-ink-faint/10 text-ink-muted border-border-strong",
  ESTIMATED: "bg-demo/10 text-demo border-demo/30",
  NEEDS_REVIEW: "bg-risk-high/10 text-risk-high border-risk-high/30",
  EXPIRED: "bg-risk-high/10 text-risk-high border-risk-high/30",
};

export default function DataStatusBadge({ status, className = "" }: Props) {
  const style = STYLES[status] || STYLES.UNVERIFIED;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${style} ${className}`}
    >
      {status}
    </span>
  );
}
