import { useTranslation } from "react-i18next";
import { useSpeech } from "../hooks/useSpeech";
import SpeakerIcon from "./icons/SpeakerIcon";

interface Props {
  /** id of the element whose visible text should be read aloud. */
  targetId?: string;
}

/**
 * Floating "read this page aloud" button. Reads the visible text content of
 * the given container (defaults to #page-main-content, which AppShell and
 * the standalone auth pages both render on their main content area), so
 * every page in the app gets a working voice/read-aloud feature, not only
 * the report page.
 */
export default function PageReadAloud({ targetId = "page-main-content" }: Props) {
  const { t } = useTranslation();
  const { status, speak } = useSpeech();

  function handleClick() {
    const el = document.getElementById(targetId);
    const text = el?.innerText ?? "";
    speak(text);
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={status === "loading"}
      title={t("voice.readPage")}
      aria-label={t("voice.readPage")}
      className="fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full border border-primary-dark bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg transition-colors hover:bg-primary-dark disabled:opacity-60"
    >
      <SpeakerIcon active={status === "playing"} />
      <span>
        {status === "loading" && t("voice.loading")}
        {status === "playing" && t("voice.stop")}
        {status === "error" && t("voice.unavailable")}
        {status === "idle" && t("voice.readPage")}
      </span>
    </button>
  );
}
