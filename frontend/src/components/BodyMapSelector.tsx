import React from 'react';
import { AlertTriangle, Check, RotateCcw } from 'lucide-react';

export type BodyRegionId = 'head' | 'chest' | 'left_arm' | 'abdomen' | 'back' | 'legs';

export interface BodyRegionConfig {
  id: BodyRegionId;
  labelEn: string;
  labelHi: string;
  symptomsEn: string;
  symptomsHi: string;
  defaultDescriptorEn: string;
  defaultDescriptorHi: string;
}

export const BODY_REGIONS: BodyRegionConfig[] = [
  {
    id: 'head',
    labelEn: 'Head / Neurological',
    labelHi: 'सिर / न्यूरोलॉजिकल',
    symptomsEn: 'Headache, dizziness, vision changes',
    symptomsHi: 'सिरदर्द, चक्कर आना, दृष्टि धुंधली होना',
    defaultDescriptorEn: 'Headache and neurological presentation reported',
    defaultDescriptorHi: 'सिर में दर्द और न्यूरोलॉजिकल लक्षण दर्ज किए गए',
  },
  {
    id: 'chest',
    labelEn: 'Chest / Precordial',
    labelHi: 'छाती / हृदय क्षेत्र',
    symptomsEn: 'Chest pain, tightness, pressure',
    symptomsHi: 'छाती में दर्द, दबाव, भारीपन, घबराहट',
    defaultDescriptorEn: 'Precordial chest discomfort and pain reported',
    defaultDescriptorHi: 'छाती में तेज दर्द और भारीपन के लक्षण दर्ज किए गए',
  },
  {
    id: 'left_arm',
    labelEn: 'Left Arm / Shoulder',
    labelHi: 'बायां हाथ / कंधा',
    symptomsEn: 'Radiating pain, shoulder numbness',
    symptomsHi: 'बाएं हाथ में दर्द का फैलाव, कंधे में सुन्नपन',
    defaultDescriptorEn: 'Left arm and shoulder radiation reported',
    defaultDescriptorHi: 'बाएं हाथ और कंधे में दर्द का प्रसार दर्ज किया गया',
  },
  {
    id: 'abdomen',
    labelEn: 'Abdomen / Epigastric',
    labelHi: 'पेट / आमाशय',
    symptomsEn: 'Abdominal pain, cramps, nausea',
    symptomsHi: 'पेट दर्द, ऐंठन, मतली, उल्टी, गैस',
    defaultDescriptorEn: 'Abdominal and epigastric tenderness reported',
    defaultDescriptorHi: 'पेट और आमाशय में दर्द और असुविधा दर्ज की गई',
  },
  {
    id: 'back',
    labelEn: 'Lower Back / Flank',
    labelHi: 'पीठ / कमर (निचला हिस्सा)',
    symptomsEn: 'Lower back stiffness, flank pain',
    symptomsHi: 'कमर दर्द, पीठ में जकड़न, रीढ़ में दर्द',
    defaultDescriptorEn: 'Lower back and lumbar pain reported',
    defaultDescriptorHi: 'कमर और पीठ के निचले हिस्से में दर्द दर्ज किया गया',
  },
  {
    id: 'legs',
    labelEn: 'Lower Limbs / Legs',
    labelHi: 'पैर / निचले अंग',
    symptomsEn: 'Leg pain, swelling, difficulty walking',
    symptomsHi: 'पैरों में दर्द, जोड़ों में सूजन, चलने में कठिनाई',
    defaultDescriptorEn: 'Lower extremities pain and swelling reported',
    defaultDescriptorHi: 'पैरों और घुटनों में दर्द व सूजन दर्ज की गई',
  },
];

export interface BodyMapSelectorProps {
  selectedRegions: string[];
  onSelectRegion: (regions: string[], descriptors: string[]) => void;
  patientLanguage?: string;
}

export const BodyMapSelector: React.FC<BodyMapSelectorProps> = ({
  selectedRegions,
  onSelectRegion,
  patientLanguage = 'hi',
}) => {
  const isSelected = (id: string) => selectedRegions.includes(id);

  // Co-selection of chest and left_arm triggers high cardiac radiation warning
  const hasCardiacRadiation =
    selectedRegions.includes('chest') && selectedRegions.includes('left_arm');

  const toggleRegion = (id: BodyRegionId) => {
    let nextRegions: string[];
    if (selectedRegions.includes(id)) {
      nextRegions = selectedRegions.filter((r) => r !== id);
    } else {
      nextRegions = [...selectedRegions, id];
    }

    const descriptors = nextRegions.map((rId) => {
      const cfg = BODY_REGIONS.find((b) => b.id === rId);
      if (!cfg) return rId;
      return patientLanguage === 'hi'
        ? `${cfg.labelHi} (${cfg.defaultDescriptorHi})`
        : `${cfg.labelEn} (${cfg.defaultDescriptorEn})`;
    });

    onSelectRegion(nextRegions, descriptors);
  };

  const handleClearAll = () => {
    onSelectRegion([], []);
  };

  return (
    <div className="w-full bg-white rounded-3xl border-2 border-slate-200 shadow-xl p-5 md:p-6 space-y-5 text-left">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-lg md:text-xl font-black text-[#0F2E4A] flex items-center gap-2">
            <span>2D Anatomical Body Map / शारीरिक दर्द चयन</span>
          </h3>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Tap painful body regions to append anatomical descriptors directly into clinical intake.
          </p>
        </div>

        {selectedRegions.length > 0 && (
          <button
            type="button"
            onClick={handleClearAll}
            className="min-h-[48px] min-w-[48px] px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold flex items-center justify-center gap-1.5 transition active:scale-95"
            title="Clear all selected regions"
          >
            <RotateCcw className="w-4 h-4 text-slate-500" />
            <span>Clear / रीसेट</span>
          </button>
        )}
      </div>

      {/* High Cardiac Radiation Alert Banner */}
      {hasCardiacRadiation && (
        <div className="p-4 bg-red-600 text-white rounded-2xl shadow-lg border-2 border-red-700 flex items-start gap-3 animate-pulse">
          <AlertTriangle className="w-6 h-6 text-yellow-300 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-black text-sm uppercase tracking-wide">
              ⚠️ High Cardiac Alert: Chest pain radiating to left arm detected. Immediate clinical assessment recommended.
            </div>
            <div className="text-xs font-semibold text-red-100">
              चेतावनी: छाती का दर्द बाएं हाथ में फैल रहा है। तत्काल ईसीजी और आपातकालीन चिकित्सा सहायता अनुशंसित है।
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Anatomical Interactive SVG Silhouette + Region Selector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        {/* Left Column: 2D Anatomical SVG Human Silhouette */}
        <div className="lg:col-span-5 bg-gradient-to-b from-slate-900 via-[#0F2E4A] to-slate-900 p-4 rounded-2xl border-2 border-blue-900/60 shadow-inner flex flex-col items-center justify-center relative">
          <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-300 mb-2">
            Interactive Body Diagram (आगे / सामने का दृश्य)
          </span>

          <svg
            viewBox="0 0 280 440"
            className="w-full max-w-[240px] h-auto select-none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Base Body Silhouette Outline (Subtle dark background figure) */}
            <g opacity="0.25" fill="#64748B">
              {/* Head */}
              <circle cx="140" cy="45" r="28" />
              {/* Neck */}
              <rect x="132" y="70" width="16" height="18" rx="4" />
              {/* Torso */}
              <path d="M 95 88 L 185 88 L 175 230 L 105 230 Z" />
              {/* Arms */}
              <path d="M 95 90 L 60 180 L 52 245 L 68 245 L 80 185 L 100 115 Z" />
              <path d="M 185 90 L 220 180 L 228 245 L 212 245 L 200 185 L 180 115 Z" />
              {/* Legs */}
              <path d="M 105 230 L 95 350 L 92 415 L 118 415 L 128 350 L 135 235 Z" />
              <path d="M 175 230 L 185 350 L 188 415 L 162 415 L 152 350 L 145 235 Z" />
            </g>

            {/* 1. Head / Neuro Region */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('head')}
            >
              <circle
                cx="140"
                cy="45"
                r="30"
                fill={isSelected('head') ? '#0284C7' : '#1E293B'}
                stroke={isSelected('head') ? '#38BDF8' : '#475569'}
                strokeWidth={isSelected('head') ? '3.5' : '1.5'}
                filter={isSelected('head') ? 'url(#glow)' : undefined}
                className="transition-colors"
              />
              <text x="140" y="49" fill="#FFFFFF" fontSize="11" fontWeight="bold" textAnchor="middle">
                HEAD
              </text>
            </g>

            {/* 2. Chest / Precordial Region */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('chest')}
            >
              <rect
                x="108"
                y="94"
                width="64"
                height="56"
                rx="10"
                fill={
                  hasCardiacRadiation
                    ? '#DC2626'
                    : isSelected('chest')
                    ? '#2563EB'
                    : '#1E293B'
                }
                stroke={
                  hasCardiacRadiation
                    ? '#F87171'
                    : isSelected('chest')
                    ? '#60A5FA'
                    : '#475569'
                }
                strokeWidth={isSelected('chest') ? '3.5' : '1.5'}
                filter={isSelected('chest') ? 'url(#glow)' : undefined}
                className="transition-colors"
              />
              <text x="140" y="126" fill="#FFFFFF" fontSize="11" fontWeight="extrabold" textAnchor="middle">
                CHEST
              </text>
            </g>

            {/* 3. Left Arm / Shoulder Region (Viewer's right side, patient's left arm) */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('left_arm')}
            >
              <path
                d="M 182 96 L 222 175 L 228 245 L 208 245 L 198 180 L 176 122 Z"
                fill={
                  hasCardiacRadiation
                    ? '#DC2626'
                    : isSelected('left_arm')
                    ? '#2563EB'
                    : '#1E293B'
                }
                stroke={
                  hasCardiacRadiation
                    ? '#F87171'
                    : isSelected('left_arm')
                    ? '#60A5FA'
                    : '#475569'
                }
                strokeWidth={isSelected('left_arm') ? '3.5' : '1.5'}
                filter={isSelected('left_arm') ? 'url(#glow)' : undefined}
                className="transition-colors"
              />
              <text x="210" y="170" fill="#FFFFFF" fontSize="10" fontWeight="bold" textAnchor="middle">
                L.ARM
              </text>
            </g>

            {/* Right Arm non-interactive silhouette */}
            <path
              d="M 98 96 L 58 175 L 52 245 L 72 245 L 82 180 L 104 122 Z"
              fill="#1E293B"
              stroke="#334155"
              strokeWidth="1.5"
            />

            {/* 4. Abdomen / Epigastric Region */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('abdomen')}
            >
              <rect
                x="110"
                y="158"
                width="60"
                height="50"
                rx="8"
                fill={isSelected('abdomen') ? '#059669' : '#1E293B'}
                stroke={isSelected('abdomen') ? '#34D399' : '#475569'}
                strokeWidth={isSelected('abdomen') ? '3.5' : '1.5'}
                filter={isSelected('abdomen') ? 'url(#glow)' : undefined}
                className="transition-colors"
              />
              <text x="140" y="188" fill="#FFFFFF" fontSize="11" fontWeight="bold" textAnchor="middle">
                ABDOMEN
              </text>
            </g>

            {/* 5. Lower Back / Flank Region */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('back')}
            >
              <rect
                x="112"
                y="214"
                width="56"
                height="32"
                rx="6"
                fill={isSelected('back') ? '#D97706' : '#1E293B'}
                stroke={isSelected('back') ? '#FBBF24' : '#475569'}
                strokeWidth={isSelected('back') ? '3.5' : '1.5'}
                filter={isSelected('back') ? 'url(#glow)' : undefined}
                className="transition-colors"
              />
              <text x="140" y="234" fill="#FFFFFF" fontSize="10" fontWeight="bold" textAnchor="middle">
                L.BACK
              </text>
            </g>

            {/* 6. Lower Limbs / Legs Region */}
            <g
              className="cursor-pointer transition-all duration-200"
              onClick={() => toggleRegion('legs')}
            >
              <g
                fill={isSelected('legs') ? '#7C3AED' : '#1E293B'}
                stroke={isSelected('legs') ? '#A78BFA' : '#475569'}
                strokeWidth={isSelected('legs') ? '3.5' : '1.5'}
                filter={isSelected('legs') ? 'url(#glow)' : undefined}
                className="transition-colors"
              >
                <path d="M 104 252 L 95 350 L 92 418 L 120 418 L 128 350 L 133 252 Z" />
                <path d="M 176 252 L 185 350 L 188 418 L 160 418 L 152 350 L 147 252 Z" />
              </g>
              <text x="140" y="340" fill="#FFFFFF" fontSize="11" fontWeight="bold" textAnchor="middle">
                LEGS
              </text>
            </g>
          </svg>

          <span className="text-[11px] text-slate-300 mt-2 font-medium text-center">
            Click diagram or choose regions below
          </span>
        </div>

        {/* Right Column: 6 Accessible Touch-Target Buttons (>=48x48px) */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {BODY_REGIONS.map((region) => {
            const active = isSelected(region.id);
            const isCardiacHighlight =
              hasCardiacRadiation && (region.id === 'chest' || region.id === 'left_arm');

            return (
              <button
                key={region.id}
                type="button"
                onClick={() => toggleRegion(region.id)}
                className={`min-h-[64px] min-w-[48px] w-full px-4 py-3 rounded-2xl border-2 text-left transition-all flex items-center justify-between gap-3 active:scale-[0.98] ${
                  isCardiacHighlight
                    ? 'bg-red-50 border-red-500 text-red-950 shadow-md ring-2 ring-red-400'
                    : active
                    ? 'bg-blue-50 border-blue-600 text-blue-950 shadow-md ring-2 ring-blue-300'
                    : 'bg-white border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 text-slate-800'
                }`}
                title={`Select ${region.labelEn}`}
              >
                <div className="space-y-0.5 min-w-0">
                  <div className="font-extrabold text-sm flex items-center gap-1.5 truncate">
                    <span>{region.labelEn}</span>
                  </div>
                  <div className="text-xs font-semibold text-slate-600 truncate">
                    {region.labelHi}
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">
                    {patientLanguage === 'hi' ? region.symptomsHi : region.symptomsEn}
                  </div>
                </div>

                <div
                  className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 border transition-colors ${
                    isCardiacHighlight
                      ? 'bg-red-600 text-white border-red-700'
                      : active
                      ? 'bg-blue-600 text-white border-blue-700'
                      : 'bg-slate-100 text-transparent border-slate-300'
                  }`}
                >
                  <Check className="w-4 h-4 stroke-[3]" />
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Regions Summary Pill Bar */}
      {selectedRegions.length > 0 && (
        <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-slate-500">Selected Regions:</span>
          {selectedRegions.map((rId) => {
            const cfg = BODY_REGIONS.find((b) => b.id === rId);
            return (
              <span
                key={rId}
                className="bg-blue-100 text-blue-900 border border-blue-300 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1"
              >
                <span>{cfg ? cfg.labelEn : rId}</span>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default BodyMapSelector;
