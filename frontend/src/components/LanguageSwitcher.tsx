import { useTranslation } from "react-i18next";
import { SUPPORTED_LANGUAGES } from "../i18n";

interface Props {
  className?: string;
}

export default function LanguageSwitcher({ className = "" }: Props) {
  const { i18n, t } = useTranslation();

  return (
    <label className={`inline-flex items-center gap-1.5 text-xs ${className}`}>
      <span className="sr-only">{t("common.language")}</span>
      <select
        value={i18n.resolvedLanguage || i18n.language || "en"}
        onChange={(e) => i18n.changeLanguage(e.target.value)}
        aria-label={t("common.language")}
        className="border border-border-strong bg-surface px-2 py-1 text-xs text-ink focus:border-primary"
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </label>
  );
}
