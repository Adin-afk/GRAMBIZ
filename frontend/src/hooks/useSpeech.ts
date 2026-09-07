import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { synthesizeSpeech } from "../api/endpoints";

export type SpeechStatus = "idle" | "loading" | "playing" | "error";

/**
 * Shared "read aloud" logic: tries the backend TTS (ElevenLabs) first, and
 * falls back to the browser's built-in speech synthesis if that's
 * unavailable (not configured on the backend, network error, or the
 * language isn't supported yet). Used by both the per-section ListenButton
 * and the page-wide PageReadAloud button so behavior stays consistent
 * everywhere voice is exposed in the app.
 */
export function useSpeech() {
  const { i18n } = useTranslation();
  const [status, setStatus] = useState<SpeechStatus>("idle");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      window.speechSynthesis?.cancel();
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    };
  }, []);

  function speakWithBrowserFallback(text: string) {
    if (!text || !("speechSynthesis" in window)) {
      setStatus("error");
      return;
    }
    try {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = i18n.resolvedLanguage || i18n.language || "en";
      utterance.onend = () => setStatus("idle");
      utterance.onerror = () => setStatus("error");
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
      setStatus("playing");
    } catch {
      setStatus("error");
    }
  }

  async function speak(text: string | null | undefined) {
    if (status === "playing") {
      audioRef.current?.pause();
      window.speechSynthesis?.cancel();
      setStatus("idle");
      return;
    }

    const clean = (text || "").replace(/\s+/g, " ").trim();
    if (!clean) {
      setStatus("error");
      return;
    }

    setStatus("loading");
    try {
      const blob = await synthesizeSpeech(clean);
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
      const url = URL.createObjectURL(blob);
      objectUrlRef.current = url;

      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => setStatus("idle");
      audio.onerror = () => speakWithBrowserFallback(clean);
      await audio.play();
      setStatus("playing");
    } catch {
      speakWithBrowserFallback(clean);
    }
  }

  function stop() {
    audioRef.current?.pause();
    window.speechSynthesis?.cancel();
    setStatus("idle");
  }

  return { status, speak, stop };
}
