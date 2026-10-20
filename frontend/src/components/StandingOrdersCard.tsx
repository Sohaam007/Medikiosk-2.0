import React from 'react';
import {
  Clock,
  MapPin,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  FlaskConical,
  ArrowRight,
} from 'lucide-react';
import type { StandingOrderResponse } from '../client/types.gen';

export interface StandingOrdersCardProps {
  standingOrders: StandingOrderResponse | null;
  isLoading?: boolean;
  onAcknowledge?: () => void;
  patientLanguage?: string;
}

export const StandingOrdersCard: React.FC<StandingOrdersCardProps> = ({
  standingOrders,
  isLoading = false,
  onAcknowledge,
  patientLanguage = 'hi',
}) => {
  if (isLoading) {
    return (
      <div className="w-full bg-white rounded-3xl border-2 border-blue-200 p-6 shadow-xl space-y-4 animate-pulse text-left">
        <div className="h-6 bg-slate-200 rounded w-1/3"></div>
        <div className="h-4 bg-slate-200 rounded w-1/2"></div>
        <div className="space-y-3 pt-3">
          <div className="h-16 bg-slate-100 rounded-2xl"></div>
          <div className="h-16 bg-slate-100 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  if (!standingOrders || !standingOrders.orders || standingOrders.orders.length === 0) {
    return (
      <div className="w-full bg-white rounded-3xl border-2 border-slate-200 p-6 shadow-md text-left flex items-start gap-3">
        <CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-extrabold text-base text-[#0F2E4A]">
            No Pre-Consultation Labs Required / पूर्व-परामर्श जांच आवश्यक नहीं
          </h4>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Standard presentation. Proceed directly to OPD consultation without diagnostic routing delay.
          </p>
        </div>
      </div>
    );
  }

  const { orders, clinical_rationale, estimated_time_saved_minutes, requires_fasting } =
    standingOrders;

  return (
    <div className="w-full bg-white rounded-3xl border-2 border-blue-300 shadow-xl p-5 md:p-6 space-y-5 text-left">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-blue-100 pb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-md shrink-0">
            <FlaskConical className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg md:text-xl font-black text-[#0F2E4A] m-0">
                Clinical Standing Orders (CSO)
              </h3>
              <span className="text-[10px] font-extrabold uppercase tracking-wider bg-blue-100 text-blue-900 px-2.5 py-0.5 rounded-full border border-blue-300">
                Pre-Consult Labs
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              प्री-कंसल्टेशन लैब जांच और डायग्नोस्टिक रूटिंग
            </p>
          </div>
        </div>

        {/* Time Saved & Fasting Badges */}
        <div className="flex flex-wrap items-center gap-2">
          {estimated_time_saved_minutes > 0 && (
            <div className="bg-emerald-50 text-emerald-900 border border-emerald-300 px-3 py-1.5 rounded-xl text-xs font-black flex items-center gap-1.5 shadow-sm">
              <Clock className="w-4 h-4 text-emerald-600" />
              <span>⏱️ Estimated {estimated_time_saved_minutes} min saved</span>
            </div>
          )}

          {requires_fasting ? (
            <span className="bg-amber-100 text-amber-900 border border-amber-300 px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
              <span>Fasting Sample Required (खाली पेट)</span>
            </span>
          ) : (
            <span className="bg-slate-100 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-slate-500" />
              <span>No Fasting Required</span>
            </span>
          )}
        </div>
      </div>

      {/* Clinical Rationale Box */}
      {clinical_rationale && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50/70 border border-blue-200 rounded-2xl flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="text-[11px] font-black uppercase tracking-wider text-blue-800">
              Clinical Rationale / नैदानिक तर्क:
            </span>
            <p className="text-xs md:text-sm font-semibold text-[#0F2E4A] leading-relaxed">
              {clinical_rationale}
            </p>
          </div>
        </div>
      )}

      {/* Orders List Grid */}
      <div className="space-y-3">
        <span className="text-xs font-extrabold uppercase tracking-wider text-slate-500 block">
          Recommended Pre-Consultation Diagnostic Tests ({orders.length})
        </span>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {orders.map((item) => {
            const isStat = item.urgency.toUpperCase() === 'STAT';

            return (
              <div
                key={item.code}
                className={`p-4 rounded-2xl border-2 flex flex-col justify-between gap-3 shadow-sm transition-all ${
                  isStat
                    ? 'bg-red-50/70 border-red-300'
                    : 'bg-slate-50/80 border-slate-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[11px] font-black bg-white px-2 py-0.5 rounded border border-slate-300 text-slate-800 shadow-2xs">
                        {item.code}
                      </span>
                      <span
                        className={`text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full ${
                          isStat
                            ? 'bg-red-600 text-white animate-pulse'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {item.urgency}
                      </span>
                    </div>

                    <h4 className="text-sm font-black text-[#0F2E4A]">
                      {item.name_en}
                    </h4>
                    <p className="text-xs font-semibold text-slate-600">
                      {item.name_hi}
                    </p>
                  </div>
                </div>

                {/* Bay / Room Location Tag */}
                <div className="pt-2 border-t border-slate-200/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5 font-bold text-slate-700">
                    <MapPin className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>Location:</span>
                    <strong className="text-[#0F2E4A] font-extrabold">{item.bay_room}</strong>
                  </div>
                  <span className="text-[10px] text-slate-500 font-semibold">
                    {patientLanguage === 'hi' ? 'पहले यहां जाएं' : 'Visit Prior to OPD'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Acknowledge Button (if provided) with >=48x48px Touch Target */}
      {onAcknowledge && (
        <div className="pt-2">
          <button
            type="button"
            onClick={onAcknowledge}
            className="w-full min-h-[52px] min-w-[48px] px-6 py-3 bg-[#0F2E4A] hover:bg-[#1E3A8A] active:bg-[#0A1F33] text-white font-extrabold text-sm rounded-2xl flex items-center justify-center gap-2 shadow-md transition active:scale-[0.98]"
          >
            <span>Proceed with Standing Orders / आदेश स्वीकार करें</span>
            <ArrowRight className="w-5 h-5 text-cyan-300" />
          </button>
        </div>
      )}
    </div>
  );
};

export default StandingOrdersCard;
