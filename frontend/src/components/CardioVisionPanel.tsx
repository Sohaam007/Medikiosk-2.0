import { useState } from 'react';

type VesselKey = 'LAD' | 'LCX' | 'RCA';

interface ScreeningResult {
  cad: { prob: number; label: number; ci?: [number, number] };
  vessels: Record<VesselKey, { prob: number; label: number }>;
  meta: { mode?: string; disclaimer?: string };
}

interface CardioVisionPanelProps {
  patientAge: string;
}

function probability(value: number) {
  return `${Math.round(value * 100)}%`;
}

function offlinePreview(age: number, hypertension: boolean, chestPain: boolean): ScreeningResult {
  const logit = -1.4 + 0.045 * (age - 55) + (hypertension ? 0.7 : 0) + (chestPain ? 0.65 : 0);
  const sigmoid = (value: number) => 1 / (1 + Math.exp(-value));
  const cad = sigmoid(logit);
  const vessels = {
    LAD: { prob: sigmoid(logit - 0.2), label: Number(sigmoid(logit - 0.2) >= 0.5) },
    LCX: { prob: sigmoid(logit - 0.7), label: Number(sigmoid(logit - 0.7) >= 0.5) },
    RCA: { prob: sigmoid(logit - 0.6), label: Number(sigmoid(logit - 0.6) >= 0.5) },
  };
  return {
    cad: { prob: Math.max(cad, ...Object.values(vessels).map((vessel) => vessel.prob)), label: Number(cad >= 0.5) },
    vessels,
    meta: {
      mode: 'offline-preview',
      disclaimer: 'Preview only; clinician review and diagnostic testing are required.',
    },
  };
}

export function CardioVisionPanel({ patientAge }: CardioVisionPanelProps) {
  const [age, setAge] = useState(patientAge || '42');
  const [hypertension, setHypertension] = useState(false);
  const [chestPain, setChestPain] = useState(false);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'offline'>('idle');

  async function runScreening() {
    const numericAge = Number(age) || 42;
    setStatus('loading');
    try {
      const token = import.meta.env.VITE_API_TOKEN as string | undefined;
      const response = await fetch('/api/screening/cardiovascular', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          features: {
            Age: numericAge,
            HTN: Number(hypertension),
            'Typical Chest Pain': Number(chestPain),
          },
        }),
      });
      if (!response.ok) throw new Error('screening service unavailable');
      setResult((await response.json()) as ScreeningResult);
      setStatus('ready');
    } catch {
      setResult(offlinePreview(numericAge, hypertension, chestPain));
      setStatus('offline');
    }
  }

  return (
    <section className="lg:col-span-12 rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-50 via-white to-sky-50 p-6 shadow-sm" aria-labelledby="cardiovision-heading">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.18em] text-indigo-700">CardioVision · Screen</p>
          <h3 id="cardiovision-heading" className="mt-1 text-xl font-black text-[#0F2E4A]">Heart-risk screening before intake</h3>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">A fast, explainable screen that helps the care team prioritize the next step. It does not diagnose disease.</p>
        </div>
        <span className="rounded-full border border-indigo-200 bg-white px-3 py-1 text-xs font-bold text-indigo-700">Offline-ready</span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-4 md:items-end">
        <label className="text-sm font-bold text-slate-700">
          Age
          <input value={age} onChange={(event) => setAge(event.target.value)} inputMode="numeric" className="mt-1 min-h-[48px] w-full rounded-xl border border-slate-300 bg-white px-3" aria-label="Screening age" />
        </label>
        <label className="flex min-h-[48px] items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-bold text-slate-700">
          <input type="checkbox" checked={hypertension} onChange={(event) => setHypertension(event.target.checked)} className="h-5 w-5" />
          History of hypertension
        </label>
        <label className="flex min-h-[48px] items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-bold text-slate-700">
          <input type="checkbox" checked={chestPain} onChange={(event) => setChestPain(event.target.checked)} className="h-5 w-5" />
          Typical chest pain
        </label>
        <button type="button" onClick={() => void runScreening()} disabled={status === 'loading'} className="min-h-[48px] rounded-xl bg-indigo-700 px-4 font-black text-white shadow-sm transition hover:bg-indigo-800 disabled:bg-slate-400">
          {status === 'loading' ? 'Screening…' : 'Run heart screen'}
        </button>
      </div>

      {result && (
        <div className="mt-5 grid gap-4 md:grid-cols-[1.2fr_1fr]" role="status" aria-live="polite">
          <div className={`rounded-2xl border p-4 ${result.cad.prob >= 0.5 ? 'border-amber-300 bg-amber-50' : 'border-emerald-300 bg-emerald-50'}`}>
            <p className="text-xs font-black uppercase tracking-widest text-slate-600">Estimated CAD screening probability</p>
            <p className="mt-1 text-4xl font-black text-[#0F2E4A]">{probability(result.cad.prob)}</p>
            <p className="mt-2 text-sm font-semibold text-slate-700">{result.cad.prob >= 0.5 ? 'Prioritize clinician review.' : 'Continue the structured intake and preventive guidance.'}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-black uppercase tracking-widest text-slate-500">Whole-vessel screening view</p>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center text-sm font-black text-slate-700">
              {(Object.keys(result.vessels) as VesselKey[]).map((vessel) => <div key={vessel} className="rounded-xl bg-slate-100 p-3"><span>{vessel}</span><br /><span className="text-lg text-indigo-700">{probability(result.vessels[vessel].prob)}</span></div>)}
            </div>
          </div>
        </div>
      )}
      {status === 'offline' && <p className="mt-3 text-xs font-bold text-indigo-700">Offline preview shown. Connect the API and repeat the screen for the configured backend result.</p>}
      {result && <p className="mt-3 text-xs text-slate-600">{result.meta.disclaimer}</p>}
    </section>
  );
}
