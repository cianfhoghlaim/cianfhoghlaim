/**
 * Anti-bot detection for determining when to fall back to cloud browser.
 * Detects Cloudflare, reCAPTCHA, Turnstile, and other protection mechanisms.
 */

import type { Page } from "playwright";

export interface AntiBotSignal {
  type: "cloudflare" | "recaptcha" | "turnstile" | "hcaptcha" | "verification_prompt" | "rate_limit" | "access_denied";
  confidence: number;
  details?: string;
}

export interface DetectionResult {
  shouldFallback: boolean;
  signals: AntiBotSignal[];
  recommendation: string;
}

/**
 * Detect anti-bot measures on the current page.
 */
export async function detectAntiBotMeasures(page: Page): Promise<DetectionResult> {
  const signals: AntiBotSignal[] = [];

  try {
    const detection = await page.evaluate(() => {
      const results: Array<{ type: string; confidence: number; details?: string }> = [];

      // Cloudflare detection
      const hasCfWrapper = !!document.querySelector("#cf-wrapper");
      const hasCfChallenge = document.cookie.includes("cf_chl_");
      const hasCfTurnstile = !!document.querySelector(".cf-turnstile");
      const cfRayHeader = document.querySelector('meta[name="cf-ray"]');

      if (hasCfWrapper || hasCfChallenge) {
        results.push({
          type: "cloudflare",
          confidence: 0.95,
          details: hasCfWrapper ? "Challenge page detected" : "Challenge cookie present",
        });
      }

      if (hasCfTurnstile) {
        results.push({
          type: "turnstile",
          confidence: 0.95,
          details: "Cloudflare Turnstile widget detected",
        });
      }

      // reCAPTCHA detection
      const hasGrecaptcha = typeof (window as any).grecaptcha !== "undefined";
      const hasRecaptchaElement = !!document.querySelector(".g-recaptcha, [data-sitekey]");
      const hasRecaptchaIframe = !!document.querySelector('iframe[src*="recaptcha"]');

      if (hasGrecaptcha || hasRecaptchaElement || hasRecaptchaIframe) {
        results.push({
          type: "recaptcha",
          confidence: 0.9,
          details: hasGrecaptcha ? "grecaptcha object present" : "reCAPTCHA element detected",
        });
      }

      // hCaptcha detection
      const hasHcaptcha = !!document.querySelector(".h-captcha, [data-hcaptcha-sitekey]");
      const hasHcaptchaIframe = !!document.querySelector('iframe[src*="hcaptcha"]');

      if (hasHcaptcha || hasHcaptchaIframe) {
        results.push({
          type: "hcaptcha",
          confidence: 0.9,
          details: "hCaptcha widget detected",
        });
      }

      // Generic verification prompts
      const bodyText = document.body.innerText.toLowerCase();
      const verificationPhrases = [
        "verify you are human",
        "please verify",
        "human verification",
        "bot detection",
        "security check",
        "prove you're not a robot",
        "complete the captcha",
      ];

      for (const phrase of verificationPhrases) {
        if (bodyText.includes(phrase)) {
          results.push({
            type: "verification_prompt",
            confidence: 0.8,
            details: `Text contains: "${phrase}"`,
          });
          break;
        }
      }

      // Access denied detection
      const accessDeniedPhrases = [
        "access denied",
        "403 forbidden",
        "blocked",
        "you have been blocked",
        "your ip has been blocked",
      ];

      for (const phrase of accessDeniedPhrases) {
        if (bodyText.includes(phrase)) {
          results.push({
            type: "access_denied",
            confidence: 0.85,
            details: `Access denied: "${phrase}"`,
          });
          break;
        }
      }

      // Rate limit detection
      const rateLimitPhrases = [
        "rate limit",
        "too many requests",
        "slow down",
        "try again later",
      ];

      for (const phrase of rateLimitPhrases) {
        if (bodyText.includes(phrase)) {
          results.push({
            type: "rate_limit",
            confidence: 0.75,
            details: `Rate limit indicator: "${phrase}"`,
          });
          break;
        }
      }

      return results;
    });

    signals.push(...(detection as AntiBotSignal[]));
  } catch (error) {
    // If we can't run detection, assume something is wrong
    console.error("[AntiBotDetector] Detection failed:", error);
    signals.push({
      type: "access_denied",
      confidence: 0.5,
      details: `Detection script failed: ${error}`,
    });
  }

  const shouldFallback = signals.some((s) => s.confidence >= 0.8);

  let recommendation = "Continue with local browser";
  if (shouldFallback) {
    const highConfidenceSignals = signals.filter((s) => s.confidence >= 0.8);
    recommendation = `Fallback recommended: ${highConfidenceSignals.map((s) => s.type).join(", ")}`;
  }

  return {
    shouldFallback,
    signals,
    recommendation,
  };
}

/**
 * Check if an error indicates we should fall back to cloud.
 */
export function isAntiBotError(error: Error | unknown): boolean {
  const errorStr = String(error).toLowerCase();

  const patterns = [
    "cloudflare",
    "captcha",
    "verify",
    "blocked",
    "403",
    "forbidden",
    "rate limit",
    "too many requests",
    "connection refused",
    "timeout",
    "econnrefused",
    "net::err",
  ];

  return patterns.some((pattern) => errorStr.includes(pattern));
}

/**
 * Check HTTP response status for fallback indicators.
 */
export function shouldFallbackOnStatus(status: number): boolean {
  // Cloudflare challenge pages
  if (status === 503 || status === 403) {
    return true;
  }
  // Rate limiting
  if (status === 429) {
    return true;
  }
  return false;
}
