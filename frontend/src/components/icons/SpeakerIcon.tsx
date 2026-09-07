export default function SpeakerIcon({ active, size = 14 }: { active: boolean; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={active ? "text-primary" : ""}
    >
      <polygon points="3 9 3 15 8 15 13 20 13 4 8 9 3 9" />
      {active ? (
        <path d="M16 8a5 5 0 0 1 0 8M19 5a9 9 0 0 1 0 14" />
      ) : (
        <line x1="16" y1="9" x2="21" y2="15" />
      )}
      {!active && <line x1="21" y1="9" x2="16" y2="15" />}
    </svg>
  );
}
