import { useTranslation } from "react-i18next";
import { useSpeech } from "../hooks/useSpeech";
import SpeakerIcon from "./icons/SpeakerIcon";

interface ListenButtonProps {
  /** The text to read aloud, already in whichever language it's displayed in. */
  text: string | null | undefined;
  className?: string;
}

/**
 * "Read aloud" button for a specific piece of text (e.g. the AI explanation
 * on the report page). Tries ElevenLabs first (via /api/voice/speak, which
 * auto-detects the language from the text itself), then falls back to the
 * browser's built-in speech synthesis rather than doing nothing.
 */
export default function ListenButton({ text, className = "" }: ListenButtonProps) {
  const { t } = useTranslation();
  const { status, speak } = useSpeech();

  if (!text || !text.trim()) return null;

  return (
    <button
      type="button"
      onClick={() => speak(text)}
      disabled={status === "loading"}
      title={status === "error" ? t("voice.unavailable") : undefined}
      className={`inline-flex items-center gap-1.5 border border-border px-2.5 py-1 text-xs font-medium text-ink-muted transition-colors hover:bg-bg disabled:opacity-50 ${className}`}
    >
      <SpeakerIcon active={status === "playing"} />
      <span>
        {status === "loading" && t("voice.loading")}
        {status === "playing" && t("voice.stop")}
        {status === "error" && t("voice.unavailable")}
        {status === "idle" && t("voice.listen")}
      </span>
    </button>
  );
}
