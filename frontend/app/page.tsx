"use client";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Copy,
  Database,
  KeyRound,
  Loader2,
  ShieldCheck,
  Sparkles,
  Terminal,
} from "lucide-react";
import { useMemo, useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { createRun } from "@/features/runs/api";
import type { PolicyMode, RunCreateResponse } from "@/features/runs/types";

const samplePrompt =
  "Analyze this production error. User email: rahul.mehra@example.com JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123.def456 Database URL: postgres://admin:mysecretpass@prod-db.internal:5432/app API key: sk-prod-92ksl29sksl29sksl29s Error: payment-service timed out after calling invoice-api.";

export default function HomePage() {
  const [input, setInput] = useState(samplePrompt);
  const [policyMode, setPolicyMode] = useState<PolicyMode>("balanced");
  const [result, setResult] = useState<RunCreateResponse | null>(null);

  const mutation = useMutation({
    mutationFn: createRun,
    onSuccess: setResult,
  });

  const entityGroups = useMemo(() => {
    if (!result) return [];

    return result.detected_entities.map((entity) => ({
      label: entity.type,
      source: entity.source,
      risk: entity.risk_level,
      action: entity.action,
      replacement: entity.replacement_value,
      confidence: Math.round(entity.confidence * 100),
    }));
  }, [result]);

  function handleRun() {
    mutation.mutate({
      input,
      policy_mode: policyMode,
      model: "gemini-2.5-flash",
    });
  }

  return (
    <DashboardShell>
      <div className="space-y-4">
        <div className="grid gap-4 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.25fr)_360px]">
          <section className="console-panel overflow-hidden">
            <PanelHeader
              icon={<Terminal className="h-4 w-4 text-cyan-300" />}
              title="Input prompt"
              subtitle="Paste the prompt or log payload you want to inspect."
            />

            <div className="p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="text-xs text-slate-500">Policy mode</div>
                <Select
                  value={policyMode}
                  onValueChange={(value) => setPolicyMode(value as PolicyMode)}
                >
                  <SelectTrigger className="h-8 w-[150px] border-white/10 bg-black/30 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monitor">Monitor</SelectItem>
                    <SelectItem value="balanced">Balanced</SelectItem>
                    <SelectItem value="strict">Strict</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                className="min-h-[420px] resize-none border-white/10 bg-black/40 font-mono text-xs leading-6 text-slate-200 placeholder:text-slate-600"
              />

              <div className="mt-4 flex items-center justify-between gap-3">
                <Button
                  variant="outline"
                  className="border-white/10 bg-transparent text-slate-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setInput(samplePrompt)}
                >
                  Load sample
                </Button>

                <Button
                  onClick={handleRun}
                  disabled={mutation.isPending || input.trim().length === 0}
                  className="bg-cyan-300 text-black hover:bg-cyan-200"
                >
                  {mutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Running
                    </>
                  ) : (
                    <>
                      Run through Blackbox
                      <Sparkles className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          </section>

          <section className="space-y-4">
            <div className="console-panel overflow-hidden">
              <PanelHeader
                icon={<ShieldCheck className="h-4 w-4 text-emerald-300" />}
                title="Protected prompt"
                subtitle="This is what gets sent to Gemini after policy enforcement."
              />

              <div className="p-4">
                <CodeBlock
                  value={
                    result?.protected_prompt ??
                    "Run Blackbox to generate a protected prompt."
                  }
                  muted={!result}
                />
              </div>
            </div>

            <div className="console-panel overflow-hidden">
              <PanelHeader
                icon={<Sparkles className="h-4 w-4 text-violet-300" />}
                title="Gemini response"
                subtitle="Model output is scanned again before being reported."
              />

              <div className="p-4">
                <CodeBlock
                  value={
                    result?.model_response ??
                    "The model response will appear here after execution."
                  }
                  muted={!result}
                  tall
                />
              </div>
            </div>
          </section>

          <aside className="space-y-4">
            <div className="console-panel overflow-hidden">
              <PanelHeader
                icon={<AlertTriangle className="h-4 w-4 text-amber-300" />}
                title="Risk report"
                subtitle="Run-level privacy summary."
              />

              <div className="space-y-3 p-4">
                <MetricRow
                  label="Run status"
                  value={result?.status ?? "not started"}
                  tone={result?.status === "completed" ? "success" : "muted"}
                />
                <MetricRow
                  label="Risk level"
                  value={result?.risk_level ?? "unknown"}
                  tone={result?.risk_level === "critical" ? "danger" : "muted"}
                />
                <MetricRow
                  label="Input entities"
                  value={String(result?.report.input_entities_count ?? 0)}
                />
                <MetricRow
                  label="Tokenized"
                  value={String(result?.report.tokenized_count ?? 0)}
                />
                <MetricRow
                  label="Response flags"
                  value={String(result?.report.flagged_response_count ?? 0)}
                />

                <Separator className="bg-white/10" />

                <div className="rounded-lg border border-white/10 bg-black/30 p-3">
                  <div className="mb-2 flex items-center gap-2 text-xs font-medium text-slate-300">
                    <Clock3 className="h-3.5 w-3.5 text-cyan-300" />
                    LLM call
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between gap-4">
                      <span className="text-slate-500">Provider</span>
                      <span className="text-slate-300">
                        {result?.llm_call?.provider ?? "—"}
                      </span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-slate-500">Model</span>
                      <span className="text-slate-300">
                        {result?.llm_call?.model_name ?? "—"}
                      </span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-slate-500">Latency</span>
                      <span className="text-slate-300">
                        {result?.llm_call?.latency_ms
                          ? `${result.llm_call.latency_ms} ms`
                          : "—"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {mutation.error ? (
              <Alert className="border-red-400/20 bg-red-400/10 text-red-200">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Run failed</AlertTitle>
                <AlertDescription>
                  {mutation.error instanceof Error
                    ? mutation.error.message
                    : "Unknown error"}
                </AlertDescription>
              </Alert>
            ) : null}

            <div className="console-panel overflow-hidden">
              <PanelHeader
                icon={<KeyRound className="h-4 w-4 text-cyan-300" />}
                title="Detected entities"
                subtitle="Sensitive values found in the current run."
              />

              <div className="max-h-[420px] space-y-2 overflow-auto p-4">
                {entityGroups.length === 0 ? (
                  <EmptyState />
                ) : (
                  entityGroups.map((entity, index) => (
                    <EntityCard key={`${entity.label}-${index}`} entity={entity} />
                  ))
                )}
              </div>
            </div>
          </aside>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <SmallStatus
            icon={<ShieldCheck className="h-4 w-4 text-emerald-300" />}
            label="Detection"
            value="Regex detector + policy engine"
          />
          <SmallStatus
            icon={<Database className="h-4 w-4 text-cyan-300" />}
            label="Persistence"
            value="Neon PostgreSQL trace storage"
          />
          <SmallStatus
            icon={<CheckCircle2 className="h-4 w-4 text-violet-300" />}
            label="Execution"
            value="Gemini 2.5 Flash via FastAPI"
          />
        </div>
      </div>
    </DashboardShell>
  );
}

function PanelHeader({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="border-b border-white/10 px-4 py-3">
      <div className="flex items-center gap-2">
        {icon}
        <div className="text-sm font-medium text-white">{title}</div>
      </div>
      <div className="mt-1 text-xs text-slate-500">{subtitle}</div>
    </div>
  );
}

function CodeBlock({
  value,
  muted,
  tall,
}: {
  value: string;
  muted?: boolean;
  tall?: boolean;
}) {
  return (
    <div
      className={[
        "overflow-auto rounded-lg border border-white/10 bg-black/40 p-3 font-mono text-xs leading-6",
        tall ? "max-h-[390px] min-h-[250px]" : "max-h-[230px] min-h-[160px]",
        muted ? "text-slate-600" : "text-slate-300",
      ].join(" ")}
    >
      <pre className="whitespace-pre-wrap break-words">{value}</pre>
    </div>
  );
}

function MetricRow({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "success" | "danger" | "muted";
}) {
  const toneClass =
    tone === "success"
      ? "text-emerald-300"
      : tone === "danger"
        ? "text-red-300"
        : tone === "muted"
          ? "text-slate-500"
          : "text-slate-200";

  return (
    <div className="flex items-center justify-between rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs">
      <span className="text-slate-500">{label}</span>
      <span className={["font-medium uppercase", toneClass].join(" ")}>
        {value}
      </span>
    </div>
  );
}

function EntityCard({
  entity,
}: {
  entity: {
    label: string;
    source: string;
    risk: string;
    action: string;
    replacement: string;
    confidence: number;
  };
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/30 p-3">
      <div className="flex items-center justify-between gap-2">
        <Badge
          variant="outline"
          className="border-cyan-400/20 bg-cyan-400/10 font-mono text-[11px] text-cyan-300"
        >
          {entity.label}
        </Badge>
        <span className="text-[11px] uppercase text-slate-500">
          {entity.risk}
        </span>
      </div>

      <div className="mt-3 space-y-1.5 text-xs">
        <div className="flex justify-between gap-4">
          <span className="text-slate-500">Action</span>
          <span className="text-slate-300">{entity.action}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-500">Source</span>
          <span className="text-slate-300">{entity.source}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-500">Confidence</span>
          <span className="text-slate-300">{entity.confidence}%</span>
        </div>
      </div>

      <div className="mt-3 rounded-md border border-white/10 bg-black/40 px-2 py-1.5 font-mono text-[11px] text-cyan-300">
        {entity.replacement}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-lg border border-dashed border-white/10 bg-black/20 p-6 text-center">
      <div className="text-sm text-slate-400">No entities yet</div>
      <div className="mt-1 text-xs text-slate-600">
        Run a prompt to populate the trace.
      </div>
    </div>
  );
}

function SmallStatus({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="console-panel-soft p-4">
      <div className="flex items-center gap-2 text-sm font-medium text-white">
        {icon}
        {label}
      </div>
      <div className="mt-1 text-xs text-slate-500">{value}</div>
    </div>
  );
}