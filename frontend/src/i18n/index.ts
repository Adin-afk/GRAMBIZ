import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en.json";
import hi from "./locales/hi.json";
import mr from "./locales/mr.json";
import asLang from "./locales/as.json";
import bn from "./locales/bn.json";
import brx from "./locales/brx.json";
import doi from "./locales/doi.json";
import gu from "./locales/gu.json";
import kn from "./locales/kn.json";
import kok from "./locales/kok.json";
import ks from "./locales/ks.json";
import mai from "./locales/mai.json";
import ml from "./locales/ml.json";
import mni from "./locales/mni.json";
import ne from "./locales/ne.json";
import orLang from "./locales/or.json";
import pa from "./locales/pa.json";
import sa from "./locales/sa.json";
import sat from "./locales/sat.json";
import sd from "./locales/sd.json";
import ta from "./locales/ta.json";
import te from "./locales/te.json";
import ur from "./locales/ur.json";

export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "mr", label: "मराठी" },
  { code: "as", label: "অসমীয়া" },
  { code: "bn", label: "বাংলা" },
  { code: "brx", label: "बड़ो" },
  { code: "doi", label: "डोगरी" },
  { code: "gu", label: "ગુજરાતી" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "kok", label: "कोंकणी" },
  { code: "ks", label: "کٲشُر" },
  { code: "mai", label: "मैथिली" },
  { code: "ml", label: "മലയാളം" },
  { code: "mni", label: "মৈতৈলোন্" },
  { code: "ne", label: "नेपाली" },
  { code: "or", label: "ଓଡ଼ିଆ" },
  { code: "pa", label: "ਪੰਜਾਬੀ" },
  { code: "sa", label: "संस्कृतम्" },
  { code: "sat", label: "ᱥᱟᱱᱛᱟᱲᱤ" },
  { code: "sd", label: "سنڌي" },
  { code: "ta", label: "தமிழ்" },
  { code: "te", label: "తెలుగు" },
  { code: "ur", label: "اردو" },
] as const;

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      mr: { translation: mr },
      as: { translation: asLang },
      bn: { translation: bn },
      brx: { translation: brx },
      doi: { translation: doi },
      gu: { translation: gu },
      kn: { translation: kn },
      kok: { translation: kok },
      ks: { translation: ks },
      mai: { translation: mai },
      ml: { translation: ml },
      mni: { translation: mni },
      ne: { translation: ne },
      or: { translation: orLang },
      pa: { translation: pa },
      sa: { translation: sa },
      sat: { translation: sat },
      sd: { translation: sd },
      ta: { translation: ta },
      te: { translation: te },
      ur: { translation: ur },
    },
    fallbackLng: "en",
    supportedLngs: SUPPORTED_LANGUAGES.map((l) => l.code),
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "sra_language",
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
