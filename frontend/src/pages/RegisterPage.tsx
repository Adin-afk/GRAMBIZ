import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../api/client";
import LanguageSwitcher from "../components/LanguageSwitcher";
import PageReadAloud from "../components/PageReadAloud";

export default function RegisterPage() {
  const { t } = useTranslation();
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({ full_name: fullName, email, password });
      navigate("/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div id="page-main-content" className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="mb-3 flex justify-end">
          <LanguageSwitcher />
        </div>

        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 h-[3px] w-16 bg-gradient-to-r from-accent via-border to-primary" />
          <h1 className="font-display text-xl font-semibold text-primary">{t("common.appName")}</h1>
        </div>

        <form onSubmit={handleSubmit} className="border border-border bg-surface p-6">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-muted">
            {t("auth.createAccount")}
          </h2>

          {error && (
            <div className="mb-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">
              {error}
            </div>
          )}

          <label className="mb-3 block text-sm">
            <span className="mb-1 block text-ink-muted">{t("auth.fullName")}</span>
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
            />
          </label>

          <label className="mb-3 block text-sm">
            <span className="mb-1 block text-ink-muted">{t("auth.email")}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
            />
          </label>

          <label className="mb-5 block text-sm">
            <span className="mb-1 block text-ink-muted">{t("auth.passwordMin")}</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
          >
            {loading ? t("auth.creatingAccount") : t("auth.createAccount")}
          </button>

          <p className="mt-4 text-center text-xs text-ink-muted">
            {t("auth.alreadyHaveAccount")}{" "}
            <Link to="/login" className="text-primary underline">
              {t("auth.signIn")}
            </Link>
          </p>
        </form>
      </div>

      <PageReadAloud />
    </div>
  );
}
